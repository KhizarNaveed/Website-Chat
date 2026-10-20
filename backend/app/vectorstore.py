import os
from langchain_chroma import Chroma
from langchain_core.documents import Document
from app.config import settings
from app.embedder import get_embedder

COLLECTION_NAME = "website_content"

def get_vectorstore() -> Chroma:
    """Return the persistent ChromaDB collection."""
    os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedder(),
        persist_directory=settings.CHROMA_PERSIST_DIR,
    )

def reset_collection() -> None:
    """Delete all existing vectors (fresh start for each URL)."""
    try:
        vs = get_vectorstore()
        vs.delete_collection()
        print("[VECTORSTORE] Cleared existing collection")
    except Exception as e:
        print(f"[VECTORSTORE] Reset skipped: {e}")

def index_documents(docs: list[Document]) -> int:
    """Add documents to ChromaDB. Resets first to avoid stale data."""
    reset_collection()
    vs = get_vectorstore()
    vs.add_documents(docs)
    print(f"[VECTORSTORE] Indexed {len(docs)} chunks")
    return len(docs)

def get_retriever(top_k: int | None = None):
    """Return a retriever for RAG."""
    k = top_k or settings.TOP_K
    vs = get_vectorstore()
    return vs.as_retriever(search_kwargs={"k": k})