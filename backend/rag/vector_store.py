import os
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from backend.config import GEMINI_API_KEY

# Initialize the embedding model (turns text into searchable math)
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", 
    google_api_key=GEMINI_API_KEY
)

# Define where to save the database locally
DB_FAISS_PATH = "backend/rag/vectorstore/db_faiss"

def create_vector_store(chunks):
    """
    Takes text chunks and saves them into a searchable FAISS database.
    """
    # Create the vector store from the chunks
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    # Save it locally so we don't have to re-process every time
    vector_store.save_local(DB_FAISS_PATH)
    
    return vector_store

def load_vector_store():
    """
    Loads the existing database from the local path.
    """
    if os.path.exists(DB_FAISS_PATH):
        return FAISS.load_local(
            DB_FAISS_PATH, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
    return None