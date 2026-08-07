from pathlib import Path
import os
import openai

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
)

from langchain_core.documents import Document

from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from vector_store import VectorStore
from config import GOOGLE_API_KEY, GEMINI_MODEL
from config import OPENAI_API_KEY, OPENAI_MODEL
from prompts import SYSTEM_PROMPT


class LLMRAGHandler:

    def __init__(self):
        # LLM will be initialized lazily (may require GOOGLE_API_KEY)
        self.llm = None

        # Initialize Vector Store
        self.vector_store = VectorStore()

        # Load all PDFs from resources folder (only once)
        self.vector_store.load_resources()

        # System Prompt
        self.system_prompt = SYSTEM_PROMPT

        # Conversation History
        self.history = [SystemMessage(content=self.system_prompt)]

        # Prompt Template
        self.rag_prompt = PromptTemplate.from_template(
            """
{system_prompt}

Conversation History:
{chat_history}

Retrieved Context:
{context}

User Question:
{input}

Answer:
"""
        )

        # Document and RAG chains are created once the LLM is available
        self.document_chain = None
        self.rag_chain = None

    def ensure_llm(self):
        """Lazily initialize the Gemini LLM and chains. Raises ValueError if API key missing."""

        if self.llm is not None:
            return

        if not GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY not set. Please set it in your environment or .env file."
            )

        # Initialize Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.3,
        )

        # Create chains
        self.document_chain = create_stuff_documents_chain(self.llm, self.rag_prompt)
        self.rag_chain = create_retrieval_chain(self.vector_store.as_retriever(), self.document_chain)

    def generate_response(self, human_message):

        print(f"\nUser : {human_message}")

        # Ensure LLM and chains are ready (will raise a clear error if API key missing)
        try:
            self.ensure_llm()
        except ValueError as exc:
            # Try OpenAI fallback if available
            if OPENAI_API_KEY:
                try:
                    openai.api_key = OPENAI_API_KEY
                    docs = self.retrieve(human_message)
                    context_text = "\n\n---\n\n".join(
                        [getattr(d, 'page_content', str(d))[:1200] for d in docs]
                    )
                    prompt = f"{self.system_prompt}\n\nRetrieved Context:\n{context_text}\n\nUser Question: {human_message}\n\nAnswer:"
                    resp = openai.ChatCompletion.create(
                        model=OPENAI_MODEL,
                        messages=[{"role":"system","content":self.system_prompt},{"role":"user","content":f"Context:\n{context_text}\n\nQuestion: {human_message}"}],
                        temperature=0.3,
                        max_tokens=512,
                    )
                    answer = resp['choices'][0]['message']['content'].strip()
                    self.history.append(HumanMessage(content=human_message))
                    self.history.append(AIMessage(content=answer))
                    return answer
                except Exception:
                    # fall through to returning retrieved context below
                    pass

            # LLMs not available — return retrieved context as a helpful fallback
            docs = self.retrieve(human_message)
            if not docs:
                return str(exc)

            snippets = []
            for d in docs:
                text = getattr(d, 'page_content', str(d))
                snippets.append(text[:1000])

            context_text = "\n\n---\n\n".join(snippets)
            return (
                "LLM unavailable: " + str(exc)
                + "\n\nRetrieved context (best matches):\n\n"
                + context_text
            )

        context_docs = self.retrieve(human_message)

        try:
            response = self.rag_chain.invoke(
                {
                    "input": human_message,
                    "context": context_docs,
                    "chat_history": self.history,
                    "system_prompt": self.system_prompt,
                }
            )

            answer = response.get("answer")

        except Exception as e:
            # Try OpenAI fallback if available
            if OPENAI_API_KEY:
                try:
                    openai.api_key = OPENAI_API_KEY
                    context_text = "\n\n---\n\n".join(
                        [getattr(d, 'page_content', str(d))[:1200] for d in context_docs]
                    )
                    resp = openai.ChatCompletion.create(
                        model=OPENAI_MODEL,
                        messages=[{"role":"system","content":self.system_prompt},{"role":"user","content":f"Context:\n{context_text}\n\nQuestion: {human_message}"}],
                        temperature=0.3,
                        max_tokens=512,
                    )
                    answer = resp['choices'][0]['message']['content'].strip()
                    self.history.append(HumanMessage(content=human_message))
                    self.history.append(AIMessage(content=answer))
                    return answer
                except Exception as e2:
                    # Return retrieved context with both errors
                    snippets = [getattr(d, 'page_content', str(d))[:1000] for d in context_docs]
                    context_text = "\n\n---\n\n".join(snippets)
                    return (
                        "LLM error: unable to generate an answer with Gemini or OpenAI. "
                        f"Gemini error: {e}; OpenAI error: {e2}\n\nRetrieved context (best matches):\n\n{context_text}"
                    )

            # If no OpenAI key or OpenAI failed, return retrieved context
            snippets = [getattr(d, 'page_content', str(d))[:1000] for d in context_docs]
            context_text = "\n\n---\n\n".join(snippets)
            return (
                "LLM error: unable to generate an answer. "
                f"Error: {e}\n\nRetrieved context (best matches):\n\n{context_text}"
            )

        self.history.append(
            HumanMessage(content=human_message)
        )

        self.history.append(
            AIMessage(content=answer)
        )

        return answer

    def reset(self):

        self.history = [
            SystemMessage(content=self.system_prompt)
        ]

    def get_history(self):

        return self.history

    def retrieve(self, question, k=4):

        return self.vector_store.similarity_search(
            question,
            k=k,
        )

    def add_pdf_to_context(self, file_path: Path):

        return self.vector_store.add_document(file_path)