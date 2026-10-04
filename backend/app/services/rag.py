from pathlib import Path
import hashlib
import pandas as pd
import chromadb
from pypdf import PdfReader
import ollama
from ..config import settings


client = chromadb.PersistentClient(path=str(Path(settings.chroma_path).resolve()))
collection = client.get_or_create_collection(name="financial_documents")
ollama_client = ollama.Client(host=settings.ollama_host)


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix == ".csv":
        return pd.read_csv(path).to_csv(index=False)
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    raise ValueError("Supported document formats: PDF, CSV, TXT, MD")


def chunk_text(text: str, size: int = 1000, overlap: int = 150):
    clean = " ".join(text.split())
    if not clean:
        return []
    chunks = []
    start = 0
    while start < len(clean):
        end = min(start + size, len(clean))
        chunks.append(clean[start:end])
        if end == len(clean):
            break
        start = end - overlap
    return chunks


def ingest(file_path: Path, user_id: int, document_id: int):
    text = extract_text(file_path)
    chunks = chunk_text(text)
    if not chunks:
        return 0
    embeddings = ollama_client.embed(model=settings.ollama_embed_model, input=chunks).embeddings
    ids = [hashlib.sha1(f"{user_id}:{document_id}:{i}".encode()).hexdigest() for i in range(len(chunks))]
    metadatas = [{"user_id": str(user_id), "document_id": str(document_id), "chunk": i} for i in range(len(chunks))]
    collection.add(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadatas)
    return len(chunks)


def search(query: str, user_id: int, n_results: int = 5):
    embedding = ollama_client.embed(model=settings.ollama_embed_model, input=query).embeddings[0]
    result = collection.query(query_embeddings=[embedding], n_results=n_results, where={"user_id": str(user_id)})
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    return [{"text": d, "metadata": m} for d, m in zip(docs, metas)]
