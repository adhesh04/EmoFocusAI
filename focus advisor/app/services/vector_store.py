# vector_store.py
# ChromaDB setup — stores and retrieves document embeddings

import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "../../chroma_db")
COLLECTION_NAME = "focus_advisor_knowledge"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Singleton — loaded once at startup, reused on every request
_embedding_model = None


def get_embedding_function():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
    return _embedding_model


def get_vector_store():
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding_function(),
        persist_directory=CHROMA_PERSIST_DIR
    )


def get_retriever(k: int = 5):
    return get_vector_store().as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": 10}
    )


def is_populated() -> bool:
    try:
        return get_vector_store()._collection.count() > 0
    except Exception:
        return False
