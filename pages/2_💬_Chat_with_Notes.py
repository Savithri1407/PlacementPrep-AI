import streamlit as st

from utils.rag import ask_question


st.title("💬 Chat with Your Notes")

st.write(
    "Ask questions based on your uploaded study materials."
)


# -----------------------------
# Chat History
# -----------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# -----------------------------
# Display Previous Messages
# -----------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])

        # Show sources for AI answers
        if (
            message["role"] == "assistant"
            and "sources" in message
        ):

            if message["sources"]:

                st.subheader("📚 Sources")

                for source in message["sources"]:
                    st.write(f"📄 {source}")


# -----------------------------
# Chat Input
# -----------------------------

question = st.chat_input(
    "Ask something about your notes..."
)


# -----------------------------
# Process Question
# -----------------------------

if question:

    # Display user question
    with st.chat_message("user"):
        st.write(question)


    # Save user question
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })


    # Generate AI response
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            answer, sources = ask_question(question)


        # Display answer
        st.write(answer)


        # Display sources
        if sources:

            st.subheader("📚 Sources")

            for source in sources:
                st.write(f"📄 {source}")


    # Save AI response and sources
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })