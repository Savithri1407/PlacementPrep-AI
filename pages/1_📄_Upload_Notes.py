import streamlit as st
import os

from utils.pdf_reader import read_pdf
from utils.text_splitter import split_text
from utils.embeddings import get_embeddings
from vectorstore.faiss_store import (
    save_vector_store,
    rebuild_vector_store
)


st.title("📄 Upload Study Materials")

st.write(
    "Upload one or more PDF files to build your study knowledge base."
)


# --------------------------------------------------
# Upload Folder
# --------------------------------------------------

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# --------------------------------------------------
# Get Embeddings
# --------------------------------------------------

embeddings = get_embeddings()


# --------------------------------------------------
# Upload Multiple PDFs
# --------------------------------------------------

uploaded_files = st.file_uploader(
    "Choose PDF Files",
    type=["pdf"],
    accept_multiple_files=True
)


# --------------------------------------------------
# Process Uploaded PDFs
# --------------------------------------------------

if uploaded_files:

    for uploaded_file in uploaded_files:

        file_path = os.path.join(
            UPLOAD_FOLDER,
            uploaded_file.name
        )

        # Save PDF
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(
            f"✅ {uploaded_file.name} uploaded successfully"
        )


        # ------------------------------------------
        # Read PDF
        # ------------------------------------------

        text = read_pdf(file_path)

        if not text.strip():

            st.error(
                f"❌ Could not extract text from "
                f"{uploaded_file.name}"
            )

            continue


        # ------------------------------------------
        # Split Text
        # ------------------------------------------

        chunks = split_text(
            text,
            uploaded_file.name
        )

        st.success(
            f"✅ {len(chunks)} chunks created from "
            f"{uploaded_file.name}"
        )


        # ------------------------------------------
        # Add to FAISS
        # ------------------------------------------

        save_vector_store(
            chunks,
            embeddings
        )

        st.success(
            f"✅ {uploaded_file.name} added to FAISS"
        )


    st.success(
        "🎉 All selected PDF files processed successfully!"
    )


# --------------------------------------------------
# Uploaded Documents
# --------------------------------------------------

st.divider()

st.subheader("📚 Uploaded Documents")


files = os.listdir(UPLOAD_FOLDER)

pdf_files = [
    file
    for file in files
    if file.lower().endswith(".pdf")
]


if pdf_files:

    for file in pdf_files:

        col1, col2 = st.columns([4, 1])


        # ------------------------------------------
        # File Name
        # ------------------------------------------

        with col1:

            st.write(
                f"📄 {file}"
            )


        # ------------------------------------------
        # Delete Button
        # ------------------------------------------

        with col2:

            if st.button(
                "🗑️ Delete",
                key=f"delete_{file}"
            ):

                file_path = os.path.join(
                    UPLOAD_FOLDER,
                    file
                )


                # Delete PDF
                os.remove(file_path)


                # Rebuild FAISS using remaining PDFs
                rebuild_vector_store(
                    embeddings
                )


                st.success(
                    f"✅ {file} deleted successfully!"
                )


                st.rerun()


else:

    st.info(
        "No PDF documents uploaded yet."
    )