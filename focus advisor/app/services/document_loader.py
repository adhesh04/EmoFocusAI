# document_loader.py
# Loads PDFs and text files, chunks them, embeds them into ChromaDB

import os
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.schema import Document
from .vector_store import get_vector_store, is_populated

logger = logging.getLogger(__name__)
KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "../knowledge_base")


def get_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )


def load_documents():
    docs = []
    if not os.path.exists(KNOWLEDGE_BASE_DIR):
        logger.warning(f"knowledge_base/ folder not found at {KNOWLEDGE_BASE_DIR}")
        return docs

    for filename in os.listdir(KNOWLEDGE_BASE_DIR):
        filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
        try:
            if filename.endswith(".txt"):
                loader = TextLoader(filepath, encoding="utf-8")
            elif filename.endswith(".pdf"):
                loader = PyPDFLoader(filepath)
            else:
                continue
            loaded = loader.load()
            for doc in loaded:
                doc.metadata["source"] = filename
            docs.extend(loaded)
            logger.info(f"Loaded: {filename} ({len(loaded)} sections)")
        except Exception as e:
            logger.error(f"Failed to load {filename}: {e}")
    return docs


def ingest(force: bool = False):
    if not force and is_populated():
        logger.info("Vector store already populated — skipping ingestion.")
        return

    logger.info("Starting knowledge base ingestion...")
    documents = load_documents()
    if not documents:
        logger.warning("No documents found in knowledge_base/")
        return

    chunks = get_splitter().split_documents(documents)
    logger.info(f"Split into {len(chunks)} chunks")

    vs = get_vector_store()
    if force:
        try:
            vs.delete_collection()
            from .vector_store import get_vector_store as rebuild
            vs = rebuild()
        except Exception:
            pass

    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        vs.add_documents(chunks[i:i + batch_size])
        logger.info(f"Embedded batch {i // batch_size + 1}/{(len(chunks) - 1) // batch_size + 1}")

    logger.info(f"Ingestion complete — {len(chunks)} chunks stored.")
