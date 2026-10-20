from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.config import settings
from app.scraper import scrape_url
from app.chunker import chunk_text
from app.vectorstore import index_documents
from app.rag import ask, clear_session, get_history

app = FastAPI(title="Chat With Any Website", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# ---------- Schemas ----------

class URLRequest(BaseModel):
    url: str

class QuestionRequest(BaseModel):
    question: str
    session_id: str = "default"

class SessionRequest(BaseModel):
    session_id: str

# ---------- Routes ----------

@app.get("/")
def root():
    return {"service": "Chat With Any Website", "model": settings.OLLAMA_MODEL}

@app.get("/health")
def health():
    return {"status": "ok", "ollama_model": settings.OLLAMA_MODEL,
            "embedding_model": settings.EMBEDDING_MODEL}

@app.post("/index")
def index_website(req: URLRequest):
    if not req.url.startswith(("http://", "https://")):
        raise HTTPException(400, "URL must start with http:// or https://")
    try:
        text = scrape_url(req.url)
        docs = chunk_text(text, req.url)
        count = index_documents(docs)
        return {"message": "Indexed", "url": req.url, "chunks": count, "chars": len(text)}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/ask")
def ask_question(req: QuestionRequest):
    if not req.question.strip():
        raise HTTPException(400, "Question cannot be empty")
    try:
        return ask(req.question, session_id=req.session_id)
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/session/clear")
def clear(req: SessionRequest):
    """Clear conversation history for a session."""
    clear_session(req.session_id)
    return {"message": f"Session {req.session_id} cleared"}

@app.get("/session/{session_id}/history")
def history(session_id: str):
    """Get conversation history for a session."""
    return {"session_id": session_id, "messages": get_history(session_id)}