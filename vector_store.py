
from pathlib import Path
import hashlib
import chromadb
import pymupdf
from sentence_transformers import SentenceTransformer


# Project directories
BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / "data" / "documents"
VECTOR_DB_DIR = BASE_DIR / "data" / "vector_db"


# Initialize the embedding model
print("Loading embedding model...")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model loaded successfully!")


# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(
    path=str(VECTOR_DB_DIR)
)

collection = chroma_client.get_or_create_collection(
    name="document_collection"
)


def extract_text(path: Path) -> str:
    """Extract text from TXT and PDF files."""

    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8")

    if path.suffix.lower() == ".pdf":
        with pymupdf.open(path) as document:
            return "\n".join(
                page.get_text() for page in document
            )

    return ""

def chunk_document(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100
) -> list[str]:
    """Split document text into overlapping chunks."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between 0 and chunk_size.")

    text = text.strip()

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks

def generate_embeddings(chunks: list[str]) -> list[list[float]]:
    """Convert document chunks into numerical vectors."""

    if not chunks:
        return []

    embeddings = embedding_model.encode(
        chunks,
        normalize_embeddings=True
    )

    return embeddings.tolist()


def index_documents() -> dict:
    """Extract, chunk, embed, and store all TXT and PDF documents."""

    indexed_files = 0
    total_chunks = 0

    for path in DOCUMENTS_DIR.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() not in {".txt", ".pdf"}:
            continue

        try:
            text = extract_text(path)
            chunks = chunk_document(text)

            if not chunks:
                continue

            embeddings = generate_embeddings(chunks)

            source_path = str(path.resolve())

            # Remove old chunks when re-indexing this document.
            collection.delete(
                where={"source_path": source_path}
            )

            ids = [
                hashlib.sha256(
                    f"{source_path}:{index}".encode("utf-8")
                ).hexdigest()
                for index in range(len(chunks))
            ]

            collection.add(
                ids=ids,
                documents=chunks,
                embeddings=embeddings,
                metadatas=[
                    {
                        "filename": path.name,
                        "source_path": source_path,
                        "chunk_index": index,
                    }
                    for index in range(len(chunks))
                ],
            )

            indexed_files += 1
            total_chunks += len(chunks)

            print(f"Indexed: {path.name} ({len(chunks)} chunks)")

        except Exception as error:
            print(f"Failed to index {path.name}: {error}")

    return {
        "indexed_files": indexed_files,
        "total_chunks": total_chunks,
    }

def search_similar_documents(
    query: str,
    n_results: int = 3
) -> list[dict]:
    """Find document chunks semantically similar to a question."""

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    total_chunks = collection.count()

    if total_chunks == 0:
        return []

    # Convert the user's question into an embedding
    query_embedding = generate_embeddings([query])[0]

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, total_chunks),
        include=["documents", "metadatas", "distances"]
    )

    matches = []

    for index, document in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][index]
        distance = results["distances"][0][index]

        matches.append({
            "filename": metadata["filename"],
            "chunk_index": metadata["chunk_index"],
            "text": document,
            "distance": distance
        })

    return matches
