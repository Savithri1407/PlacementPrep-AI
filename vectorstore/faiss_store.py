import json
import os
import shutil

import numpy as np
from langchain_core.documents import Document


VECTOR_DB = "vectorstore/local_index"
LEGACY_VECTOR_DB = "vectorstore/faiss_index"
VECTORS_FILE = "vectors.npy"
DOCUMENTS_FILE = "documents.json"


class LocalVectorStore:
    def __init__(self, embeddings, vectors, documents):
        self.embeddings = embeddings
        self.vectors = np.asarray(vectors, dtype=np.float32)
        self.documents = documents

        if self.vectors.ndim != 2 or len(self.vectors) != len(self.documents):
            raise ValueError("Vector index data is invalid or inconsistent.")

    @classmethod
    def from_documents(cls, documents, embeddings):
        if not documents:
            raise ValueError("Cannot create a vector index without documents.")

        vectors = embeddings.embed_documents(
            [document.page_content for document in documents]
        )
        return cls(embeddings, vectors, list(documents))

    def add_documents(self, documents):
        if not documents:
            return

        vectors = np.asarray(
            self.embeddings.embed_documents(
                [document.page_content for document in documents]
            ),
            dtype=np.float32,
        )

        if vectors.ndim != 2 or vectors.shape[1] != self.vectors.shape[1]:
            raise ValueError("New document embeddings do not match the vector index.")

        self.vectors = np.concatenate((self.vectors, vectors), axis=0)
        self.documents.extend(documents)

    def save_local(self, folder_path):
        os.makedirs(folder_path, exist_ok=True)
        np.save(os.path.join(folder_path, VECTORS_FILE), self.vectors)

        with open(
            os.path.join(folder_path, DOCUMENTS_FILE),
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                [
                    {
                        "page_content": document.page_content,
                        "metadata": document.metadata,
                    }
                    for document in self.documents
                ],
                file,
                ensure_ascii=False,
            )

    @classmethod
    def load_local(cls, folder_path, embeddings):
        vectors = np.load(
            os.path.join(folder_path, VECTORS_FILE),
            allow_pickle=False,
        )
        with open(
            os.path.join(folder_path, DOCUMENTS_FILE),
            "r",
            encoding="utf-8",
        ) as file:
            documents = [
                Document(
                    page_content=item["page_content"],
                    metadata=item["metadata"],
                )
                for item in json.load(file)
            ]

        return cls(embeddings, vectors, documents)

    def similarity_search(self, query, k=4):
        if not self.documents or k <= 0:
            return []

        query_vector = np.asarray(
            self.embeddings.embed_query(query),
            dtype=np.float32,
        )
        if query_vector.ndim != 1 or query_vector.shape[0] != self.vectors.shape[1]:
            raise ValueError("Query embedding does not match the vector index.")

        vector_norms = np.linalg.norm(self.vectors, axis=1)
        query_norm = np.linalg.norm(query_vector)
        denominators = vector_norms * query_norm
        scores = np.divide(
            self.vectors @ query_vector,
            denominators,
            out=np.zeros_like(vector_norms),
            where=denominators != 0,
        )
        best_indices = np.argsort(scores)[-k:][::-1]
        return [self.documents[index] for index in best_indices]


def _uploaded_pdf_chunks():
    from utils.pdf_reader import read_pdf
    from utils.text_splitter import split_text

    upload_folder = "uploads"
    if not os.path.exists(upload_folder):
        return []

    chunks = []
    pdf_files = sorted(
        file
        for file in os.listdir(upload_folder)
        if file.lower().endswith(".pdf")
    )

    for file in pdf_files:
        text = read_pdf(os.path.join(upload_folder, file))
        if text.strip():
            chunks.extend(split_text(text, file))

    return chunks


def save_vector_store(chunks, embeddings):
    if os.path.exists(VECTOR_DB):
        vector_db = LocalVectorStore.load_local(VECTOR_DB, embeddings)
        vector_db.add_documents(chunks)
    else:
        documents = _uploaded_pdf_chunks() if os.path.exists(LEGACY_VECTOR_DB) else chunks
        if not documents:
            return
        vector_db = LocalVectorStore.from_documents(documents, embeddings)

    vector_db.save_local(VECTOR_DB)


def load_vector_store(embeddings):
    if os.path.exists(VECTOR_DB):
        return LocalVectorStore.load_local(VECTOR_DB, embeddings)

    if os.path.exists(LEGACY_VECTOR_DB):
        documents = _uploaded_pdf_chunks()
        if not documents:
            raise RuntimeError(
                "The existing FAISS index cannot be loaded because its native "
                "library is blocked by Windows Application Control, and there "
                "are no uploaded PDFs available to rebuild it."
            )

        vector_db = LocalVectorStore.from_documents(documents, embeddings)
        vector_db.save_local(VECTOR_DB)
        return vector_db

    return None


def rebuild_vector_store(embeddings):
    if os.path.exists(VECTOR_DB):
        shutil.rmtree(VECTOR_DB)

    documents = _uploaded_pdf_chunks()
    if not documents:
        return

    vector_db = LocalVectorStore.from_documents(documents, embeddings)
    vector_db.save_local(VECTOR_DB)
