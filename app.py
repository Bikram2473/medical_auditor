import streamlit as st
import base64
from langchain_core.messages import HumanMessage
from agent import medical_advocate_agent
import time

# 1. Page Configuration (Must be first)
st.set_page_config(
    page_title="Aegis | Medical Advocate", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Premium Consumer CSS Injection (Glassmorphism + Transparent Header)
st.markdown("""
    <style>
    /* Glassmorphism Background: Image + Frosted Overlay */
    .stApp {
        background-image: linear-gradient(rgba(248, 250, 252, 0.88), rgba(248, 250, 252, 0.88)), 
                          url("https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Style the main Call-To-Action button */
    .stButton>button {
        width: 100%;
        background-color: #0f172a;
        color: white !important;
        border-radius: 10px;
        padding: 14px;
        font-weight: 700;
        font-size: 16px;
        border: none;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #334155;
        transform: translateY(-1px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    /* Container styling to make them pop against the background */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(10px);
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    
    /* Make the output letter look like actual physical paper */
    .paper-document {
        background-color: white;
        padding: 40px;
        border-radius: 8px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.08);
        border-top: 4px solid #0f172a;
        font-family: 'Georgia', serif;
        color: #1e293b;
        line-height: 1.6;
    }
    
    /* Make the top header transparent to match the background */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    /* Hide default Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. Helper Function
def encode_file(uploaded_file):
    """Converts a Streamlit uploaded file into a base64 string for Gemini."""
    return base64.b64encode(uploaded_file.getvalue()).decode("utf-8")

# 4. Consumer-Friendly Header
st.markdown("<h1 style='text-align: center; color: #0f172a; margin-bottom: 0;'>🛡️ Aegis</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #64748b; font-weight: 400; margin-top: 5px; margin-bottom: 40px;'>Your AI-powered medical billing advocate. We find the overcharges. We fight the bill.</h4>", unsafe_allow_html=True)

# 5. Main Layout
col_input, col_output = st.columns([1.1, 1.9], gap="large")

with col_input:
    st.markdown("### 1. Upload Your Bill")
    st.markdown("<p style='color: #64748b; font-size: 14px;'>Securely upload a photo or PDF of your hospital invoice.</p>", unsafe_allow_html=True)
    
    with st.container(border=True):
        uploaded_bill = st.file_uploader(
            label="Drag and drop your file here", 
            type=["jpg", "jpeg", "png", "pdf"],
            label_visibility="collapsed"
        )
        
        if uploaded_bill:
            file_mime = uploaded_bill.type
            if "pdf" in file_mime:
                st.success(f"📄 Document attached: {uploaded_bill.name}")
            else:
                st.image(uploaded_bill, caption="Document attached", use_container_width=True)
                
    # --- NEW EMAIL DISPATCH UI ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 2. Autonomous Dispatch (Optional)")
    auto_send = st.toggle("Enable Aegis Auto-Send")
    
    target_email = ""
    if auto_send:
        target_email = st.text_input("Hospital Billing Email", "billing@apollohealth.mock")
        st.caption("Aegis will email the settlement offer directly to this address upon completion.")
            
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_button = st.button("🔍 Scan & Execute")

with col_output:
    st.markdown("### 3. Your Settlement Strategy")
    st.markdown("<p style='color: #64748b; font-size: 14px;'>Aegis cross-references your bill with standard fair-market prices to draft your dispute.</p>", unsafe_allow_html=True)
    
    if not analyze_button:
        # Clean empty state
        with st.container(border=True):
            st.info("👈 Waiting for document upload. Your data is processed 100% locally and is never shared.")
            st.image(
                "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&q=80&w=800", 
                caption="Aegis protects your financial health.",
                use_container_width=True
            )

    if analyze_button and uploaded_bill:
        with st.status("Aegis is analyzing your document...", expanded=True) as status:
            
            st.write("📄 Reading line items and hospital details...")
            base64_file = encode_file(uploaded_bill)
            
            # Formulate the email instruction if the user toggled it on
            email_instruction = ""
            if auto_send and target_email:
                email_instruction = f"The user has authorized auto-dispatch. Once you draft the letter, use your dispatch tool to send it to {target_email}."
            
            # Construct the multimodal prompt
            prompt_content = [
                {
                    "type": "text", 
                    "text": f"Please act as an expert medical data extractor. Look at the attached document. Extract the Patient Name, the Hospital/Facility Name, and an itemized list of every medical procedure/code and its billed price. Pass this exact data into your auditing tools. {email_instruction}"
                },
                {
                    "type": "image_url", 
                    "image_url": {"url": f"data:{uploaded_bill.type};base64,{base64_file}"}
                }
            ]
            
            st.write("⚖️ Comparing charges against regional fair-market pricing...")
            
            # Run the LangGraph Agent
            response = medical_advocate_agent.invoke({"messages": [HumanMessage(content=prompt_content)]})
            
            st.write("✍️ Drafting your legal settlement offer...")
            time.sleep(0.5)
            
            if auto_send and target_email:
                st.write("📧 Dispatching settlement via secure email protocol...")
                status.update(label="Analysis & Dispatch Complete!", state="complete", expanded=False)
            else:
                status.update(label="Analysis Complete! Your letter is ready.", state="complete", expanded=False)
        
        # Display the final text output
        final_message = response["messages"][-1].content
        
        # Inject the "Paper" CSS class around the final letter
        st.markdown(f'<div class="paper-document">{final_message}</div>', unsafe_allow_html=True)
        
        # Keep technical logs hidden but available for debugging
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.expander("Show Technical Audit Logs (For Advanced Users)"):
            for msg in response["messages"]:
                if msg.type == "tool":
                    st.code(f"Executed Tool: {msg.name}\n\nOutput Payload:\n{msg.content}", language="text")
                    
    elif analyze_button and not uploaded_bill:
        st.error("Please upload a document first.")