from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Ollama (Local LLM)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma3:4b"

    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Vector Store
    CHROMA_PERSIST_DIR: str = "../data/chroma_db"

    # Chunking (INCREASED TO 2000 FOR FASTER INDEXING)
    CHUNK_SIZE: int = 2000
    CHUNK_OVERLAP: int = 200

    # Retrieval
    TOP_K: int = 4

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

# Resolve ChromaDB path relative to backend folder
_settings_path = Path(__file__).resolve().parent.parent.parent / "data" / "chroma_db"
_settings_path.mkdir(parents=True, exist_ok=True)
settings.CHROMA_PERSIST_DIR = str(_settings_path)

print(f"[CONFIG] Ollama: {settings.OLLAMA_MODEL}")
print(f"[CONFIG] Embeddings: {settings.EMBEDDING_MODEL}")
print(f"[CONFIG] ChromaDB: {settings.CHROMA_PERSIST_DIR}")
print(f"[CONFIG] Chunk Size: {settings.CHUNK_SIZE}")