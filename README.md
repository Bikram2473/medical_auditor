# 🛡️ Aegis Medical Auditor (Agentic AI)

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Glassmorphism-red.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic-green.svg)
![DuckDB](https://img.shields.io/badge/DuckDB-Data_Mart-yellow.svg)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_RAG-purple.svg)
![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-orange.svg)

**Aegis** is an autonomous, local-first consumer advocacy agent built to detect medical billing fraud, upcoding, and severe overcharges. 

Going far beyond a simple wrapper or chatbot, Aegis is a stateful **action agent** powered by LangGraph and Gemini 2.5 Flash. It natively ingests unstructured photos or PDFs of medical bills, maps sloppy hospital shorthand to official codes using Semantic RAG, audits charges against a local DuckDB data mart, and autonomously emails a legally sound dispute letter directly to the hospital's billing department.

---

## ✨ Enterprise-Grade Features

### 👁️ Multimodal Vision Extraction
Typing line items manually is terrible UX. Aegis allows users to drag and drop PDFs, JPGs, or PNGs of their hospital bills. Utilizing Gemini's native multimodal capabilities, the agent autonomously "reads" the document to extract patient data, hospital names, and line items—bypassing the need for clunky OCR libraries like Tesseract.

### 🧠 Semantic RAG Engine (Code Mapping)
Real medical bills are messy (e.g., `EMRG RM VST LEV 3`). Standard SQL lookups fail on messy data. Aegis implements a **Retrieval-Augmented Generation (RAG)** pipeline using **ChromaDB**. It converts sloppy billing text into mathematical vectors, runs a similarity search against a database of official medical procedures, and perfectly maps the text to the correct 5-digit CPT code.

### 📊 Local Data Lakehouse (DuckDB)
Financial data never leaves the user's machine. Aegis features a local ETL pipeline into a **DuckDB Star Schema**.
* **Fact Table:** Tracks historical billing discrepancies and overcharges.
* **Dimension Tables:** Contextualizes data by Hospital, CPT Code, and Date.

### 📧 Autonomous SMTP Dispatch
Generating a text file is helpful, but true automation means handling the confrontation. Upon completing the financial audit, Aegis can securely log into a local SMTP server and automatically email the legally drafted settlement offer directly to the hospital's billing department on the user's behalf.

### 🎨 Premium "SaaS" UI (Glassmorphism)
The frontend completely overrides standard Streamlit styling. It features a custom Glassmorphism aesthetic with a frosted-glass translucent overlay, a transparent navigation header, and a dynamic CSS class that renders the agent's output as a crisp, physical piece of paper.

---

## 🏗️ System Architecture Flow

1. **Ingestion Layer:** User uploads a PDF/Image via the Glassmorphism UI.
2. **Vision Layer:** LangGraph Agent reads the image and extracts unstructured text.
3. **Semantic Layer:** ChromaDB vectorizes the messy text and maps it to official CPT codes.
4. **Data Layer:** DuckDB audits the mapped CPT codes against regional fair-market pricing.
5. **Execution Layer:** The Agent drafts the legal dispute.
6. **Dispatch Layer:** The Agent uses the built-in SMTP tool to email the letter.

---

## 🚀 Installation & Setup Guide

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/aegis-medical-auditor.git](https://github.com/YOUR_USERNAME/aegis-medical-auditor.git)
cd aegis-medical-auditor
```

### 2. Setup the Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
.\venv\Scripts\Activate.ps1  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a secure .env file in the root directory. You must use a Google App Password, not your standard email passoword, to enable the secure SMTP dispatch
```bash
# .env
GOOGLE_API_KEY=your_gemini_api_key_here
SENDER_EMAIL=your_email@gmail.com
SENDER_APP_PASSWORD=your_16_character_app_password
```

### 5. Initialize the Data Infrastructure
Before running the app, you must build both the local DuckDB database and the ChromaDB Vector database.
```bash
# Build the DuckDB Star Schema
python database.py

# Build the ChromaDB Vector Embeddings
python vector_db.py
```

### 6. Launch the Application
```bash
streamlit run app.py
```

Open your web browser to http://localhost:8501 to start auditing.

## 📸 Demo Screenshots
![**_image_alt_**](https://github.com/Bikram2473/medical_auditor/blob/main/Screenshot%202026-05-28%20133603.png)</br>
