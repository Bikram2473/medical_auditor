import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from tools import process_and_load_bill, draft_negotiation_letter

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)
advocate_tools = [process_and_load_bill, draft_negotiation_letter]

advocate_prompt = """
You are an expert Medical Billing Data Engineer and Consumer Advocate in India.

Workflow:
1. When a user provides a medical bill, extract the hospital name, the list of CPT codes, and the list of billed amounts.
2. Immediately use the `process_and_load_bill` tool to run the ETL pipeline and calculate discrepancies.
3. If discrepancies are found, use the `draft_negotiation_letter` tool to generate a dispute letter utilizing the exact audit findings.
4. Present the user with the final formatted letter. Do not include extra commentary before or after the letter.
"""

medical_advocate_agent = create_react_agent(llm, advocate_tools, prompt=advocate_prompt)