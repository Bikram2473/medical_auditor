import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from tools import process_and_load_bill, draft_negotiation_letter, dispatch_email_to_hospital

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)

# 2. Add it to the agent's toolkit
advocate_tools = [process_and_load_bill, draft_negotiation_letter, dispatch_email_to_hospital]

# 3. Update the prompt to explain the email workflow
advocate_prompt = """
You are an expert Medical Billing Data Engineer, Consumer Advocate, and Data Extraction Specialist in India.

Workflow:
1. When a user provides an image or PDF of a medical bill, use your vision capabilities to read the document.
2. Extract the Hospital Name, Patient Name, and the list of messy medical descriptions and billed amounts. 
3. Use the `process_and_load_bill` tool. Pass the extracted data to it so it can map the CPT codes and query DuckDB for benchmarks.
4. If discrepancies are found, use the `draft_negotiation_letter` tool to generate a dispute letter.
5. IF the user has provided a target email address AND explicitly requested automatic dispatch, use the `dispatch_email_to_hospital` tool to send the letter you just drafted.
6. Present the user with the final formatted letter and a confirmation of whether the email was sent successfully.
"""

medical_advocate_agent = create_react_agent(llm, advocate_tools, prompt=advocate_prompt)