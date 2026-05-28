import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

load_dotenv()

# We use Google's embedding model to convert text into mathematical vectors
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
CHROMA_PATH = "chroma_data"

def initialize_vector_db():
    """
    Creates a local ChromaDB instance and loads it with official 
    medical procedures and their corresponding CPT codes as metadata.
    """
    print("Initializing ChromaDB Vector Embeddings...")
    
    # Official Medical Dictionary (In production, this would be thousands of codes)
    official_procedures = [
        Document(
            page_content="Specialist Consultation (Complex) Extended Office Visit",
            metadata={"cpt_code": "99214"}
        ),
        Document(
            page_content="Comprehensive Metabolic Panel Bloodwork Lab Test",
            metadata={"cpt_code": "80053"}
        ),
        Document(
            page_content="Chest X-Ray Single View Frontal Radiograph",
            metadata={"cpt_code": "71045"}
        ),
        Document(
            page_content="Emergency Room Visit Level 3 Moderate Severity",
            metadata={"cpt_code": "99283"}
        )
    ]
    
    # Create the vector database locally
    vector_store = Chroma.from_documents(
        documents=official_procedures,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    
    print(f"[SUCCESS] Vector Database built at ./{CHROMA_PATH}")

if __name__ == "__main__":
    initialize_vector_db()