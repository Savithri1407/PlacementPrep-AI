from vectorstore.faiss_store import load_vector_store
from utils.embeddings import get_embeddings
from utils.gemini import get_answer


def ask_question(question):

    embeddings = get_embeddings()

    vector_db = load_vector_store(embeddings)

    if vector_db is None:
        return "Please upload a PDF first.", []


    docs = vector_db.similarity_search(
        question,
        k=3
    )


    context = ""

    sources = []


    for doc in docs:

        context += doc.page_content + "\n\n"

        source = doc.metadata.get(
            "source",
            "Unknown"
        )

        if source not in sources:
            sources.append(source)


    answer = get_answer(
        context,
        question
    )


    return answer, sources