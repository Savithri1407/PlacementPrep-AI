import streamlit as st
import os


st.set_page_config(
    page_title="PrepGenius AI",
    page_icon="🤖",
    layout="wide"
)


# -----------------------------
# Home Page
# -----------------------------

st.title("🤖 PrepGenius AI")

st.subheader(
    "AI-Powered Interview Preparation Platform"
)

st.divider()

st.write(
    "Welcome to PrepGenius AI! "
    "Prepare for technical and placement interviews "
    "using your own study materials and Generative AI."
)


# -----------------------------
# Count Uploaded PDFs
# -----------------------------

upload_folder = "uploads"

if os.path.exists(upload_folder):

    pdf_count = len([
        file
        for file in os.listdir(upload_folder)
        if file.lower().endswith(".pdf")
    ])

else:

    pdf_count = 0


# -----------------------------
# Dashboard
# -----------------------------

st.subheader("📊 Dashboard")

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "📚 Study Materials",
        pdf_count
    )


with col2:

    st.metric(
        "💬 AI Chat",
        "Ready"
    )


with col3:

    st.metric(
        "🤖 RAG System",
        "Active"
    )


st.divider()


# -----------------------------
# Features
# -----------------------------

st.subheader("🚀 Features")


col1, col2 = st.columns(2)


with col1:

    st.markdown(
        """
        ### 📚 Study Materials

        Upload Java, DBMS, OS, DSA,
        Networking and other placement notes.

        ### 💬 Chat with Notes

        Ask questions from your uploaded
        study materials using RAG.
        """
    )


with col2:

    st.markdown(
        """
        ### 🎤 Mock Interview

        Practice technical interview
        questions with AI.

        ### 📄 Resume Analyzer

        Upload your resume and get
        AI-powered interview preparation.
        """
    )


st.divider()

st.info(
    "💡 Start by uploading your study materials "
    "from the Upload Notes section."
)