from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.config import settings

def chunk_text(text: str, source_url: str) -> list[Document]:
    """Split scraped text into overlapping chunks with source metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
    )

    chunks = splitter.split_text(text)

    docs = [
        Document(
            page_content=chunk.strip(),
            metadata={"source": source_url, "chunk_id": i}
        )
        for i, chunk in enumerate(chunks)
        if chunk.strip()
    ]

    print(f"[CHUNKER] Created {len(docs)} chunks (size={settings.CHUNK_SIZE}, overlap={settings.CHUNK_OVERLAP})")
    return docs