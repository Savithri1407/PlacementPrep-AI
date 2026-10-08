from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text(text, source):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.create_documents(
        [text],
        metadatas=[
            {
                "source": source
            }
        ]
    )

    return chunks