import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def process_document(file_path):
    """
    Step 1: Identify the file type and load the content.
    Step 2: Split the text into smaller chunks for the RAG system.
    """
    # 1. Choose the correct loader based on the file extension
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".txt"):
        loader = TextLoader(file_path)
    else:
        return "Unsupported file format. Please use PDF or TXT."

    # 2. Extract the text from the file
    documents = loader.load()

    # 3. Split the text into chunks
    # We use 1000 characters with a small overlap so no information is cut in half.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=150
    )
    
    chunks = text_splitter.split_documents(documents)
    
    return chunks
