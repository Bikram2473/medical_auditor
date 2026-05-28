import streamlit as st
from langchain_core.messages import HumanMessage
from agent import medical_advocate_agent
import time

# 1. Page Configuration
st.set_page_config(
    page_title="Aegis | Medical Advocate", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Theme-Agnostic Custom CSS
# We only style the button and containers so it adapts to your Dark/Light mode safely
st.markdown("""
    <style>
    /* Style the main execute button */
    .stButton>button {
        width: 100%;
        background-color: #0056b3;
        color: white !important;
        border-radius: 8px;
        padding: 12px;
        font-weight: 600;
        font-size: 16px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #004494;
        box-shadow: 0 4px 12px rgba(0,86,179,0.3);
    }
    </style>
""", unsafe_allow_html=True)

# 3. App Header & Subtitle
st.title("🛡️ Aegis Medical Auditor")
st.markdown(
    "**Your autonomous financial defender.** Upload your billing codes below. "
    "Aegis will cross-reference regional fair-market rates, log discrepancies into your private data mart, and draft a legally sound negotiation letter."
)
st.divider()

# 4. Main Application Layout (2 Columns)
col_input, col_output = st.columns([1.2, 1.8], gap="large")

with col_input:
    st.subheader("📋 Patient & Bill Details")
    
    with st.container(border=True):
        patient = st.text_input("Patient Legal Name", "Ravi Kumar")
        hospital = st.text_input("Hospital / Facility Name", "Apollo Healthcare")
        account = st.text_input("Account / Invoice Number", "ACC-998273")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Itemized Line Items (Code & Price)**")
        raw_bill_input = st.text_area(
            "Paste CPT codes and billed amounts here:", 
            value="99214 - ₹3500.00\n80053 - ₹2800.00\n71045 - ₹1500.00",
            height=200,
            help="Format: [Code] - [Price]. Ensure each item is on a new line."
        )
    
    # The trigger button is placed right below the inputs
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_button = st.button("🚀 Execute Audit & Generate Appeal")

with col_output:
    st.subheader("🤖 Agent Output & Negotiation Document")
    
    if not analyze_button:
        # Placeholder state before the user clicks the button
        st.info("👈 Enter your bill details and click 'Execute Audit' to begin the analysis.")
        st.image(
            "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&q=80&w=800", 
            caption="Aegis operates 100% locally to protect your medical privacy.",
            use_container_width=True
        )

    if analyze_button:
        # Fancy status container for processing
        with st.status("Initializing Aegis Agentic Workflow...", expanded=True) as status:
            st.write("🔍 Parsing unstructured bill data...")
            time.sleep(0.5)
            
            prompt = (
                f"Please audit this bill for patient {patient} at {hospital} (Acct: {account}).\n"
                f"Raw Bill Data:\n{raw_bill_input}"
            )
            
            st.write("⚖️ Querying local DuckDB Data Mart for fair-market benchmarks...")
            
            # Run the LangGraph Agent
            response = medical_advocate_agent.invoke({"messages": [HumanMessage(content=prompt)]})
            
            st.write("📝 Drafting negotiation strategy...")
            time.sleep(0.5)
            status.update(label="Audit Complete & Letter Generated!", state="complete", expanded=False)
        
        # Display the final results
        final_message = response["messages"][-1].content
        
        # Wrap the letter inside a clean bordered card
        with st.container(border=True):
            st.markdown(final_message)
            
        # Hide the raw tool execution logs in an expander for a cleaner UI
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🛠️ Developer View: Inspect Agent Tool Logs"):
            for msg in response["messages"]:
                if msg.type == "tool":
                    st.code(f"Executed Tool: {msg.name}\n\nOutput Payload:\n{msg.content}", language="text")