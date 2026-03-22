import os
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from backend.config import GEMINI_API_KEY

# Initialize embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GEMINI_API_KEY
)

# Path for FAISS DB
DB_FAISS_PATH = "backend/rag/vectorstore/db_faiss"


def create_vector_store(chunks):
    """
    Create and save FAISS vector store.
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(DB_FAISS_PATH), exist_ok=True)

        vector_store = FAISS.from_documents(chunks, embeddings)
        vector_store.save_local(DB_FAISS_PATH)

        return vector_store

    except Exception as e:
        print(f"❌ Error creating vector store: {e}")
        return None


def load_vector_store():
    """
    Load FAISS vector store if exists.
    """
    try:
        if os.path.exists(DB_FAISS_PATH):
            return FAISS.load_local(
                DB_FAISS_PATH,
                embeddings,
                allow_dangerous_deserialization=True
            )
        return None

    except Exception as e:
        print(f"❌ Error loading vector store: {e}")
        return None