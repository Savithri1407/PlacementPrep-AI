import logging
from pathlib import Path
from typing import List

import bs4
import faiss

from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_community.document_loaders import (
    PyPDFLoader,
    WebBaseLoader,
)

from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import VectorStoreRetriever

from config import (
    EMBEDDING_MODEL,
    VECTOR_DB_PATH,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)

logging.basicConfig(level=logging.INFO)


class VectorStore:

    def __init__(
        self,
        vector_store_path=VECTOR_DB_PATH,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    ):

        self.vector_store_path = Path(vector_store_path)

        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL
        )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self._setup_vector_store()

    def _setup_vector_store(self):

        if self.vector_store_path.exists():

            logging.info("Loading existing FAISS index...")

            self.vector_store = FAISS.load_local(
                str(self.vector_store_path),
                embeddings=self.embeddings,
                allow_dangerous_deserialization=True,
            )

        else:

            logging.info("Creating new FAISS index...")

            dimension = len(
                self.embeddings.embed_query("PlacementPrep AI")
            )

            index = faiss.IndexFlatL2(dimension)

            self.vector_store = FAISS(
                embedding_function=self.embeddings,
                index=index,
                docstore=InMemoryDocstore(),
                index_to_docstore_id={},
            )

            self.vector_store.save_local(
                str(self.vector_store_path)
            )

    def load_document(
        self,
        pdf_path: Path,
    ) -> List[Document]:

        loader = PyPDFLoader(str(pdf_path))

        docs = loader.load()

        return docs

    def load_documents(
        self,
        folder_path,
    ) -> List[Document]:

        documents = []

        for pdf in Path(folder_path).glob("*.pdf"):

            logging.info(f"Loading {pdf.name}")

            docs = self.load_document(pdf)

            documents.extend(docs)

        return documents

    def chunk_documents(
        self,
        documents: List[Document],
    ) -> List[Document]:

        splitter = RecursiveCharacterTextSplitter(

            chunk_size=self.chunk_size,

            chunk_overlap=self.chunk_overlap,

            separators=[
                "\n\n",
                "\n",
                ".",
                " ",
                "",
            ],
        )

        return splitter.split_documents(documents)
    def add_documents(
        self,
        documents: List[Document],
    ) -> List[Document]:
    
        chunks = self.chunk_documents(documents)
    
        self.vector_store.add_documents(chunks)
    
        self.vector_store.save_local(
            str(self.vector_store_path)
        )
    
        logging.info(f"Indexed {len(chunks)} chunks.")
    
        return chunks
    

    def add_document(
        self,
        pdf_path: Path,
    ) -> List[Document]:

        documents = self.load_document(pdf_path)

        return self.add_documents(documents)


    def similarity_search(
        self,
        question: str,
        k: int = 4,
    ) -> List[Document]:

        return self.vector_store.similarity_search(
            question,
            k=k,
        )


    def as_retriever(self) -> VectorStoreRetriever:

        return self.vector_store.as_retriever(
            search_kwargs={
                "k": 4
            }
        )


    def website_to_documents(
        self,
        urls: list[str],
    ) -> List[Document]:

        loader = WebBaseLoader(

            web_paths=urls,

            bs_kwargs=dict(

                parse_only=bs4.SoupStrainer(

                    class_=(
                        "post-content",
                        "post-title",
                        "post-header",
                    )

                )

            ),

        )

        documents = loader.load()

        return documents


    def index_websites(
        self,
        urls: list[str],
    ) -> List[Document]:

        documents = self.website_to_documents(urls)

        return self.add_documents(documents)


    def load_resources(
        self,
        resource_folder="resources",
    ):

        resource_path = Path(resource_folder)

        if not resource_path.exists():

            logging.warning(
                "Resources folder not found."
            )

            return

        pdfs = list(resource_path.glob("*.pdf"))

        if len(pdfs) == 0:

            logging.warning(
                "No PDFs found inside resources."
            )

            return

        logging.info(
            f"Loading {len(pdfs)} placement PDFs..."
        )

        documents = self.load_documents(resource_path)

        self.add_documents(documents)

        logging.info(
            "Placement knowledge base created successfully."
        )