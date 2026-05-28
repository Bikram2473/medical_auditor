import duckdb
import uuid
from datetime import date
from langchain_core.tools import tool

DB_FILE = "medical_lakehouse.db"

@tool
def process_and_load_bill(hospital_name: str, cpt_codes: list[str], billed_amounts: list[float]) -> str:
    """
    An ETL tool that queries the Data Mart for benchmark rates, calculates billing discrepancies, 
    and loads the new records into the fact_billing_discrepancy table.
    """
    conn = duckdb.connect(DB_FILE)
    hospital_id = str(uuid.uuid4())[:8]
    today = date.today()
    
    # Load Dimension Data
    conn.execute("INSERT OR IGNORE INTO dim_hospital VALUES (?, ?, 'Unknown');", (hospital_id, hospital_name))
    conn.execute("INSERT OR IGNORE INTO dim_date VALUES (?, ?, ?);", (today, today.year, today.month))
    
    audit_summary = []
    total_discrepancy = 0.0
    
    # Extract, Transform, and Load Fact Data
    for code, billed in zip(cpt_codes, billed_amounts):
        benchmark_query = conn.execute("SELECT benchmark_rate, description FROM dim_cpt_code WHERE cpt_code = ?", (code,)).fetchone()
        
        if benchmark_query:
            fair_rate, description = benchmark_query
            discrepancy = billed - fair_rate if billed > fair_rate else 0.0
            total_discrepancy += discrepancy
            
            conn.execute("""
                INSERT INTO fact_billing_discrepancy VALUES (?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4())[:8], hospital_id, code, today, billed, discrepancy))
            
            audit_summary.append(f"* **CPT {code} ({description}):** Billed **₹{billed:.2f}** | Benchmark: **₹{fair_rate:.2f}** | Overcharge: **₹{discrepancy:.2f}**")
        else:
            audit_summary.append(f"* **CPT {code}:** Unknown code in dimension table. Requires manual review.")
            
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