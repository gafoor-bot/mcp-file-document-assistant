import pytest
import server


@pytest.fixture
def temp_documents_dir(tmp_path, monkeypatch):
    """Keep test files and database isolated from real project data."""
    monkeypatch.setattr(server, "DOCUMENTS_DIR", tmp_path)
    monkeypatch.setattr(
        server.database,
        "DATABASE_PATH",
        tmp_path / "test.db"
    )
    server.database.init_db()
    return tmp_path


def test_create_and_read_file(temp_documents_dir):
    server.create_file("test.txt", "Hello from MCP!")
    assert server.read_file("test.txt") == "Hello from MCP!"


def test_search_files(temp_documents_dir):
    server.create_file("employee_handbook.txt", "PTO policy")
    server.create_file("project_notes.txt", "MCP project")

    assert server.search_files("employee") == ["employee_handbook.txt"]


def test_update_file(temp_documents_dir):
    server.create_file("notes.txt", "Old content")
    server.update_file("notes.txt", "Updated content")

    assert server.read_file("notes.txt") == "Updated content"


def test_create_rejects_existing_file(temp_documents_dir):
    server.create_file("notes.txt", "Original")

    with pytest.raises(FileExistsError):
        server.create_file("notes.txt", "Replacement")

    assert server.read_file("notes.txt") == "Original"


def test_read_rejects_missing_file(temp_documents_dir):
    with pytest.raises(ValueError):
        server.read_file("missing.txt")

def test_ask_documents_finds_relevant_passage(temp_documents_dir):

    (temp_documents_dir / "employee_handbook.txt").write_text(
        "Employees receive 15 days of paid time off annually.\n"
        "Remote employees attend a weekly team meeting every Monday.",
        encoding="utf-8",
    )

    results = server.ask_documents(
        "How many paid vacation days do employees receive each year?"
    )

    assert len(results) > 0
    assert results[0]["source"] == "employee_handbook.txt"
    assert "15 days of paid time off" in results[0]["passage"]
