from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from app.llm import get_llm
from app.vectorstore import get_retriever

# In-memory session store: {session_id: [{"role": ..., "content": ...}, ...]}
SESSIONS: dict[str, list[dict]] = {}

MAX_HISTORY_TURNS = 5  # Keep last 5 Q&A pairs (10 messages)

PROMPT_WITH_HISTORY = """You are a helpful AI assistant answering questions about a website's content.

Use the CONVERSATION HISTORY below to understand follow-up questions and context.
Use the RETRIEVED CONTEXT to answer factually. If the answer isn't in the context, say:
"I don't have enough information in the provided content to answer that."

---
CONVERSATION HISTORY:
{history}

---
RETRIEVED CONTEXT:
{context}

---
CURRENT QUESTION: {question}

Answer:"""

def _format_docs(docs):
    return "\n\n---\n\n".join(d.page_content for d in docs)

def _format_history(session_id: str) -> str:
    """Format conversation history as readable text."""
    if session_id not in SESSIONS or not SESSIONS[session_id]:
        return "(No previous conversation)"

    # Keep only last N turns
    recent = SESSIONS[session_id][-MAX_HISTORY_TURNS * 2:]
    lines = []
    for msg in recent:
        role = "User" if msg["role"] == "user" else "Assistant"
        lines.append(f"{role}: {msg['content']}")
    return "\n".join(lines)

def ask(question: str, session_id: str = "default") -> dict:
    """Run RAG with conversation memory."""
    retriever = get_retriever()
    llm = get_llm()

    # 1. Retrieve relevant chunks
    source_docs = retriever.invoke(question)
    context = _format_docs(source_docs)

    # 2. Get conversation history for this session
    history = _format_history(session_id)

    # 3. Build the prompt with both history and context
    prompt = PromptTemplate(
        template=PROMPT_WITH_HISTORY,
        input_variables=["history", "context", "question"],
    )

    chain = prompt | llm | StrOutputParser()

    print(f"[RAG] Session: {session_id} | Q: {question}")
    answer = chain.invoke({
        "history": history,
        "context": context,
        "question": question,
    }).strip()

    # 4. Save this exchange to session history
    SESSIONS.setdefault(session_id, [])
    SESSIONS[session_id].append({"role": "user", "content": question})
    SESSIONS[session_id].append({"role": "assistant", "content": answer})

    # 5. Trim history to prevent unbounded growth
    if len(SESSIONS[session_id]) > MAX_HISTORY_TURNS * 2:
        SESSIONS[session_id] = SESSIONS[session_id][-MAX_HISTORY_TURNS * 2:]

    # 6. Prepare sources
    sources = [
        {
            "source": d.metadata.get("source", "Unknown"),
            "chunk_id": d.metadata.get("chunk_id", -1),
            "snippet": d.page_content[:250].strip() + "...",
        }
        for d in source_docs
    ]

    return {"answer": answer, "sources": sources}


def clear_session(session_id: str) -> None:
    """Clear conversation history for a session."""
    if session_id in SESSIONS:
        del SESSIONS[session_id]
        print(f"[RAG] Cleared session: {session_id}")


def get_history(session_id: str) -> list[dict]:
    """Return the full conversation history for a session."""
    return SESSIONS.get(session_id, [])