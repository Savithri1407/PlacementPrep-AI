# 🎯 PlacementPrep AI

## AI-Powered Placement Preparation Chatbot using RAG

PlacementPrep AI is an intelligent chatbot that helps students prepare for technical interviews by answering questions from placement study materials using **Retrieval-Augmented Generation (RAG)**.

The application allows users to upload placement preparation PDFs such as DSA, DBMS, Operating Systems, Computer Networks, Java, SQL, Aptitude, and HR Interview Notes. It retrieves the most relevant content using semantic search and generates accurate answers using an LLM.

---

## 🚀 Features

- 📚 Upload multiple placement preparation PDFs
- 🔍 Semantic search using FAISS
- 🤖 AI-powered question answering
- 💬 Interactive chat interface
- 🌐 Support for website indexing
- 💾 Persistent conversation history
- ⚡ Fast document retrieval using vector embeddings

---

## 📂 Supported Study Materials

- Data Structures & Algorithms
- Database Management Systems
- Operating Systems
- Computer Networks
- Java Programming
- Object-Oriented Programming
- SQL
- Aptitude
- HR Interview Questions
- Resume Preparation

---

## 🛠️ Technologies Used

- Python
- Streamlit
- LangChain
- FAISS
- HuggingFace Embeddings
- Ollama / Gemini API
- Vector Search (RAG)

---

## 🏗️ Project Architecture

```
User
   │
   ▼
Streamlit UI
   │
   ▼
LangChain
   │
   ▼
FAISS Vector Store
   │
   ▼
LLM (Gemini / Ollama)
   │
   ▼
Answer Generation
```

## 🚀 Setup & Run

1. Create and activate a virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Create a `.env` file from `.env.example` and set your Gemini/Google API key (if using Gemini):

```text
GOOGLE_API_KEY=your_gemini_api_key_here
```

3. Run the Streamlit app:

```powershell
.\.venv\Scripts\python -m streamlit run src/chat_ui.py
```

If you don't have a Gemini/Google API key, the app will still allow uploading and indexing documents, but answering via Gemini will be disabled until you provide the key.

## 🧩 Backend API (optional React frontend)

Start the FastAPI backend (recommended when using the React frontend):

```powershell
.venv\Scripts\python -m uvicorn src.api:app --reload --port 8000
```

The React frontend lives in `frontend/`. To run it locally:

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://localhost:8000` by default. Use `VITE_API_BASE` env var to change the API base.

