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

