import duckdb
import uuid
from datetime import date
from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

DB_FILE = "medical_lakehouse.db"
CHROMA_PATH = "chroma_data"

# Initialize the vector search connection
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vector_store = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

@tool
def process_and_load_bill(hospital_name: str, messy_descriptions: list[str], billed_amounts: list[float]) -> str:
    """
    An ETL tool that uses Semantic RAG to map messy bill text to official CPT codes, 
    queries DuckDB for fair-market rates, and calculates discrepancies.
    """
    conn = duckdb.connect(DB_FILE)
    hospital_id = str(uuid.uuid4())[:8]
    today = date.today()
    
    conn.execute("INSERT OR IGNORE INTO dim_hospital VALUES (?, ?, 'Unknown');", (hospital_id, hospital_name))
    conn.execute("INSERT OR IGNORE INTO dim_date VALUES (?, ?, ?);", (today, today.year, today.month))
    
    audit_summary = []
    total_discrepancy = 0.0
    
    for messy_text, billed in zip(messy_descriptions, billed_amounts):
        # 1. SEMANTIC SEARCH: Map messy text to the official CPT code
        search_results = vector_store.similarity_search(messy_text, k=1)
        
        if search_results:
            official_cpt = search_results[0].metadata["cpt_code"]
            
            # 2. FINANCIAL AUDIT: Query DuckDB for the benchmark rate
            benchmark_query = conn.execute("SELECT benchmark_rate, description FROM dim_cpt_code WHERE cpt_code = ?", (official_cpt,)).fetchone()
            
            if benchmark_query:
                fair_rate, description = benchmark_query
                discrepancy = billed - fair_rate if billed > fair_rate else 0.0
                total_discrepancy += discrepancy
                
                # 3. LOAD: Insert into Data Mart
                conn.execute("""
                    INSERT INTO fact_billing_discrepancy VALUES (?, ?, ?, ?, ?, ?)
                """, (str(uuid.uuid4())[:8], hospital_id, official_cpt, today, billed, discrepancy))
                
                audit_summary.append(f"* **Original Text:** '{messy_text}' -> **Mapped CPT:** {official_cpt} ({description})\n  Billed: **₹{billed:.2f}** | Benchmark: **₹{fair_rate:.2f}** | Overcharge: **₹{discrepancy:.2f}**")
            else:
                audit_summary.append(f"* **Original Text:** '{messy_text}' -> Mapped CPT {official_cpt} not found in pricing database.")
        else:
            audit_summary.append(f"* Could not map messy text: '{messy_text}'")
            
    conn.close()
    
    audit_summary.append(f"\n**Total Negotiable Discrepancy: ₹{total_discrepancy:.2f}**")
    return "\n".join(audit_summary)

@tool
def draft_negotiation_letter(patient_name: str, hospital_name: str, account_number: str, audit_findings: str) -> str:
    """
    Drafts a formal, assertive negotiation letter to the hospital using the Data Mart audit findings.
    """
    letter = (
        f"**FORMAL BILLING DISPUTE & SETTLEMENT OFFER**\n\n"
        f"**To:** Billing Department, {hospital_name}\n"
        f"**Patient:** {patient_name} | **Account:** {account_number}\n\n"
        f"To Whom It May Concern,\n\n"
        f"I am writing to formally dispute the charges on the above-referenced account. "
        f"An independent audit of the CPT codes billed reveals significant deviations from standard fair-market benchmarks and regional pricing norms.\n\n"
        f"**Audit Findings & Overcharges:**\n{audit_findings}\n\n"
        f"Under standard consumer protection guidelines and fair billing practices, I am offering to settle this account immediately for the fair-market value of the services rendered, provided the remaining balance is adjusted and the account is not forwarded to collections.\n\n"
        f"Please provide an itemized response addressing these specific discrepancies within 14 days.\n\n"
        f"Sincerely,\n{patient_name}"
    )
    return letter

@tool
def dispatch_email_to_hospital(hospital_email: str, patient_name: str, letter_body: str) -> str:
    """
    Sends the formal dispute letter to the hospital's billing department via email.
    """
    sender_email = os.getenv("SENDER_EMAIL")
    app_password = os.getenv("SENDER_APP_PASSWORD")

    if not sender_email or not app_password:
        return "Error: Email credentials not configured in the .env file. Email aborted."

    # Construct the Email
    msg = MIMEMultipart()
    msg['FROM'] = sender_email
    msg['TO'] = hospital_email
    msg['SUBJECT'] = f"FORMAL BILLING DISPUT & SETTLEMENT OFFER - Patient: {patient_name}"

    msg.attach(MIMEText(letter_body, 'plain'))

    # Securely connect and send
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        return f"[SUCCESS] The formal dispute was successfully dispatched to {hospital_email}"
    except Exception as e:
        return f"[FAILED] Could not send email: {str(e)}" 