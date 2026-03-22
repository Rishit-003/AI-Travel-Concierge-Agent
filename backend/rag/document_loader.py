import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def process_document(file_path):
    """
    Step 1: Identify the file type and load the content.
    Step 2: Split the text into smaller chunks for the RAG system.
    """

    try:
        # 0. Check if file exists
        if not os.path.exists(file_path):
            return None

        # 1. Choose loader
        if file_path.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif file_path.endswith(".txt"):
            loader = TextLoader(file_path)
        else:
            return None  # safer than returning string

        # 2. Load documents
        documents = loader.load()

        # 3. Split text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150
        )

        chunks = text_splitter.split_documents(documents)

        return chunks

    except Exception as e:
        print(f"❌ Error processing document: {e}")
        return None