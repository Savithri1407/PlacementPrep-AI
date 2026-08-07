import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage
from llm_rag import LLMRAGHandler
from conversation import ConversationManager
from pathlib import Path

# -----------------------------
# Process Uploaded PDFs
# -----------------------------
def process_new_pdfs(uploaded_files):
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = set()

    for file in uploaded_files:
        if file.name in st.session_state.processed_files:
            continue

        save_path = UPLOAD_DIR / file.name

        with save_path.open("wb") as f:
            f.write(file.read())

        st.sidebar.success(f"✅ {file.name} uploaded successfully.")

        with st.spinner(f"Indexing {file.name}..."):
            st.session_state.llm.add_pdf_to_context(save_path)

        st.session_state.processed_files.add(file.name)
        st.sidebar.success(f"✅ {file.name} indexed successfully.")
        st.rerun()


conversation_manager = ConversationManager()

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="PlacementPrep AI",
    page_icon="🎯",
    layout="wide"
)

# -----------------------------
# Header
# -----------------------------
st.title("🎯 PlacementPrep AI")

st.markdown("""
### AI Placement Preparation Chatbot

Ask questions from your placement preparation materials using
**Retrieval-Augmented Generation (RAG)**.

**Supported Topics**
- 📘 Data Structures & Algorithms
- 💾 DBMS
- 💻 Operating Systems
- 🌐 Computer Networks
- ☕ Java Programming
- 🧩 OOPs
- 🗄️ SQL
- 📝 Aptitude
- 💼 HR Interview Questions
""")

# -----------------------------
# Upload Directory
# -----------------------------
UPLOAD_DIR = Path("uploaded_pdfs")
UPLOAD_DIR.mkdir(exist_ok=True)

# -----------------------------
# Initialize LLM
# -----------------------------
if "llm" not in st.session_state:
    st.session_state.llm = LLMRAGHandler()

    saved_conversation = conversation_manager.load()

    if saved_conversation:
        st.session_state.llm.history = saved_conversation

if "processed_files" not in st.session_state:
    st.session_state.processed_files = {
        p.name for p in UPLOAD_DIR.glob("*.pdf")
    }

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("📂 PlacementPrep AI")

st.sidebar.markdown("### 📚 Study Materials")

if st.session_state.processed_files:

    for pdf in sorted(st.session_state.processed_files):
        st.sidebar.markdown(f"✅ {pdf}")

else:
    st.sidebar.info("No study materials uploaded.")

st.sidebar.divider()

st.sidebar.header("📤 Upload Study PDFs")

uploaded_files = st.sidebar.file_uploader(
    "Choose one or more PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    process_new_pdfs(uploaded_files)

st.sidebar.divider()

st.sidebar.header("🌐 Add Study Website")

urls = st.sidebar.text_area(
    "Paste website URLs (one per line)"
).splitlines()

if st.sidebar.button("Index Websites"):

    with st.spinner("Indexing websites..."):
        st.session_state.llm.vector_store.index_websites(urls)

    st.sidebar.success("✅ Website indexed successfully.")

st.sidebar.divider()

if st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state.llm.reset()
    conversation_manager.clear()
    st.rerun()

# -----------------------------
# Chat
# -----------------------------
user_input = st.chat_input(
    "Ask me about DSA, DBMS, OS, CN, Java, SQL, Aptitude, HR..."
)

if user_input:

    with st.spinner("Searching study materials..."):
        st.session_state.llm.generate_response(user_input)

conversation_manager.save(st.session_state.llm.get_history())

# -----------------------------
# Display Conversation
# -----------------------------
for msg in st.session_state.llm.get_history():

    if isinstance(msg, SystemMessage):
        continue

    role = "user" if isinstance(msg, HumanMessage) else "assistant"

    with st.chat_message(role):
        st.markdown(msg.content)