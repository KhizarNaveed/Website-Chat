from langchain_community.embeddings import HuggingFaceEmbeddings
from app.config import settings

_embedder_instance = None

def get_embedder() -> HuggingFaceEmbeddings:
    """Singleton embedder — loads model once, reuses across requests."""
    global _embedder_instance

    if _embedder_instance is None:
        print(f"[EMBEDDER] Loading model: {settings.EMBEDDING_MODEL} (first call may take 10-30 sec)")
        _embedder_instance = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        print("[EMBEDDER] Model loaded successfully")

    return _embedder_instance