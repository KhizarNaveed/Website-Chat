from langchain_ollama import ChatOllama
from app.config import settings

_llm_instance = None

def get_llm() -> ChatOllama:
    """Return a singleton ChatOllama instance."""
    global _llm_instance

    if _llm_instance is None:
        print(f"[LLM] Initializing Ollama model: {settings.OLLAMA_MODEL}")
        _llm_instance = ChatOllama(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0.3,
        )

    return _llm_instance