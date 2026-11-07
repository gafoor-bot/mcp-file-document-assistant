
from pathlib import Path
import pymupdf
import vector_store
from mcp.server.fastmcp import FastMCP
import database
import claude_client
# Create the MCP server as a global variable
mcp = FastMCP("File Document Assistant")
database.init_db()
BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / "data" / "documents"
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)


@mcp.tool()
def search_files(query: str) -> list[str]:
    """Search document filenames by keyword."""
    return [
        str(path.relative_to(DOCUMENTS_DIR))
        for path in DOCUMENTS_DIR.rglob("*")
        if path.is_file() and query.lower() in path.name.lower()
    ]
@mcp.tool()
def index_document(file_name: str) -> str:
    """Index an existing document's metadata in SQLite."""
    if not file_name or Path(file_name).name != file_name:
        raise ValueError("Provide a filename without directories.")

    path = (DOCUMENTS_DIR / file_name).resolve()

    if not path.is_relative_to(DOCUMENTS_DIR):
        raise ValueError("Access outside the documents directory is denied.")

    if not path.is_file():
        raise FileNotFoundError(f"Document not found: {file_name}")

    database.index_document(str(path))
    return f"Indexed {file_name}"


@mcp.tool()
def list_documents() -> list[dict]:
    """List document metadata stored in SQLite."""
    return database.list_documents()
@mcp.tool()
def update_file(file_name: str, new_content: str) -> str:
    """Replace the contents of an existing text document safely."""

    if not file_name or Path(file_name).name != file_name:
        raise ValueError("Provide a filename without directories.")

    if not file_name.endswith(".txt"):
        raise ValueError("Only .txt files are supported.")

    path = (DOCUMENTS_DIR / file_name).resolve()

    if not path.is_relative_to(DOCUMENTS_DIR):
        raise ValueError("Access outside the documents directory is denied.")

    if not path.is_file():
        raise FileNotFoundError(f"Document not found: {file_name}")

    path.write_text(new_content, encoding="utf-8")
    database.index_document(str(path))
    return f"Updated {file_name}"


@mcp.tool()
def read_file(file_name: str) -> str:
    """Read a text document from the documents directory."""
    path = (DOCUMENTS_DIR / file_name).resolve()

    if not path.is_relative_to(DOCUMENTS_DIR) or not path.is_file():
        raise ValueError("Document not found or access denied.")

    return path.read_text(encoding="utf-8")


@mcp.tool()
def create_file(file_name: str, content: str) -> str:
    """Create a new text document."""
    if not file_name or Path(file_name).name != file_name:
        raise ValueError("Provide a filename without directories.")

    if not file_name.endswith(".txt"):
        raise ValueError("Only .txt files are supported.")

    path = (DOCUMENTS_DIR / file_name).resolve()

    if path.exists():
        raise FileExistsError(f"{file_name} already exists.")

    path.write_text(content, encoding="utf-8")
    database.index_document(str(path))
    return f"Created {file_name}"


@mcp.tool()
def extract_pdf(file_name: str) -> str:
    """Extract text from a PDF in the approved documents folder."""

    if not file_name or Path(file_name).name != file_name:
        raise ValueError("Provide a PDF filename without directories.")

    if not file_name.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are supported.")

    path = (DOCUMENTS_DIR / file_name).resolve()

    if not path.is_relative_to(DOCUMENTS_DIR):
        raise ValueError("Access outside the documents directory is denied.")

    if not path.is_file():
        raise FileNotFoundError(f"PDF not found: {file_name}")

    with pymupdf.open(path) as document:
        text = "\n".join(page.get_text() for page in document)

    if not text.strip():
        return "No extractable text found. This PDF may contain scanned images."

    return text


@mcp.tool()
def search_document_content(query: str) -> list[dict]:
    """Search inside TXT and PDF documents."""

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    results = []
    search_term = query.casefold()

    for path in DOCUMENTS_DIR.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() not in {".txt", ".pdf"}:
            continue

        try:
            content = extract_document_text(path)
        except Exception:
            continue

        for line_number, line in enumerate(
            content.splitlines(), start=1
        ):
            if search_term in line.casefold():
                results.append({
                    "filename": path.name,
                    "line_number": line_number,
                    "text": line.strip()
                })

    return results


@mcp.tool()
def ask_documents(question: str) -> list[dict]:
    """Find document passages relevant to a natural-language question."""
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    stop_words = {
        "what", "how", "many", "does", "do", "the", "a", "an",
        "is", "are", "of", "to", "in", "for", "each", "every",
        "year", "annually", "employees", "employee", "receive",
        "get", "can", "i", "we", "they", "their"
    }

    keywords = {
        word.strip(".,?!:;").casefold()
        for word in question.split()
    } - stop_words

    results = []

    for path in DOCUMENTS_DIR.rglob("*.txt"):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue

        for line_number, line in enumerate(lines, start=1):
            text = line.strip()
            if not text:
                continue

            matched = [
                word for word in keywords
                if word in text.casefold()
            ]

            if matched:
                results.append({
                    "source": path.name,
                    "line_number": line_number,
                    "passage": text,
                    "matched_keywords": matched,
                    "match_count": len(matched)
                })

    results.sort(
        key=lambda item: item["match_count"],
        reverse=True
    )

    return results[:5]

def extract_document_text(path: Path) -> str:
    """Extract text from supported TXT and PDF documents."""

    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8")

    if path.suffix.lower() == ".pdf":
        with pymupdf.open(path) as document:
            return "\n".join(
                page.get_text() for page in document
            )

    return ""


@mcp.tool()
def ask_documents_with_claude(question: str) -> dict:
    """Answer questions using Claude and local document content."""

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    # Extract useful keywords from the question
    stop_words = {
        "what", "how", "many", "does", "do", "the", "a", "an",
        "is", "are", "of", "to", "in", "for", "each", "every",
        "year", "annually", "employees", "employee", "receive",
        "get", "can", "i", "we", "they", "their", "vacation"
    }

    keywords = [
        word.strip(".,?!:;").casefold()
        for word in question.split()
        if word.strip(".,?!:;").casefold() not in stop_words
    ]

    # Search using individual keywords
    search_results = []

    for keyword in keywords:
        matches = search_document_content(keyword)

        for match in matches:
            if match not in search_results:
                search_results.append(match)

    if not search_results:
        return {
            "answer": "I could not find relevant information in the documents.",
            "sources": []
        }

    # Prepare document context
    context_parts = []

    for result in search_results[:5]:
        context_parts.append(
            f"Source: {result['filename']}\n"
            f"Line: {result['line_number']}\n"
            f"Content: {result['text']}"
        )

    context = "\n\n".join(context_parts)

    # Ask Claude to generate the answer
    answer = claude_client.generate_answer(question, context)

    return {
        "answer": answer,
        "sources": [
            {
                "filename": result["filename"],
                "line_number": result["line_number"]
            }
            for result in search_results[:5]
        ]
    }


@mcp.tool()
def ask_documents_semantically(question: str) -> dict:
    """Answer questions using semantic search and Claude AI."""

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    # Step 1: Retrieve relevant passages from ChromaDB
    results = vector_store.search_similar_documents(
        query=question,
        n_results=5
    )

    if not results:
        return {
            "answer": "No relevant information found in the documents.",
            "sources": []
        }

    # Step 2: Prepare context for Claude
    context_parts = []

    for result in results:
        context_parts.append(
            f"Source: {result['filename']}\n"
            f"Chunk: {result['chunk_index']}\n"
            f"Content: {result['text']}"
        )

    context = "\n\n".join(context_parts)

    # Step 3: Generate an answer using Claude
    answer = claude_client.generate_answer(
        question=question,
        context=context
    )

    # Step 4: Return answer and source references
    sources = [
        {
            "filename": result["filename"],
            "chunk_index": result["chunk_index"],
            "distance": round(result["distance"], 4)
        }
        for result in results
    ]

    return {
        "answer": answer,
        "sources": sources
    }

if __name__ == "__main__":
    mcp.run()
