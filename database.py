
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "data" / "database" / "documents.db"


def init_db():
    """Create the document metadata table if it doesn't exist."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL UNIQUE,
                file_type TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)


def index_document(file_path: str):
    """Store or refresh metadata for a document."""
    path = Path(file_path).resolve()

    if not path.is_file():
        raise FileNotFoundError(f"Document not found: {path}")

    now = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("""
            INSERT INTO documents (
                filename, file_path, file_type, size_bytes,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(file_path) DO UPDATE SET
                filename = excluded.filename,
                file_type = excluded.file_type,
                size_bytes = excluded.size_bytes,
                updated_at = excluded.updated_at
        """, (
            path.name,
            str(path),
            path.suffix.lstrip(".").lower(),
            path.stat().st_size,
            now,
            now
        ))


def list_documents() -> list[dict]:
    """Return document metadata from SQLite."""
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute("""
            SELECT id, filename, file_path, file_type,
                   size_bytes, created_at, updated_at
            FROM documents
            ORDER BY filename
        """).fetchall()

    return [dict(row) for row in rows]


if __name__ == "__main__":
    init_db()
    print(f"Database initialized: {DATABASE_PATH}")
