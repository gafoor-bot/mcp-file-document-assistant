
import json
import re
import time
from pathlib import Path

import pymupdf
import claude_client
import vector_store


# Project paths
BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / "data" / "documents"
REPORT_PATH = BASE_DIR / "comparison_results.json"


# Questions used for all three approaches
QUESTIONS = [
    "What was Amazon's total revenue in 2025?",
    "What are Amazon's major business segments?",
    "What risks does Amazon identify in its annual report?",
    "What programming languages do I know?",
    "How much paid time off do employees receive?"
]


STOP_WORDS = {
    "what", "how", "many", "does", "do", "the", "a", "an",
    "is", "are", "of", "to", "in", "for", "each", "every",
    "year", "annually", "employees", "employee", "receive",
    "get", "can", "i", "we", "they", "their", "was", "were",
    "and", "or", "my", "me", "about", "identify"
}


def extract_text(path):
    """Extract text from TXT and PDF documents."""

    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8")

    if path.suffix.lower() == ".pdf":
        with pymupdf.open(path) as document:
            return "\n".join(
                page.get_text() for page in document
            )

    return ""


def retrieve_by_keywords(question, top_k=5):
    """Retrieve passages using keyword matching."""

    keywords = {
        word for word in re.findall(
            r"[a-z0-9]+", question.casefold()
        )
        if word not in STOP_WORDS and len(word) > 1
    }

    matches = []

    for path in DOCUMENTS_DIR.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() not in {".txt", ".pdf"}:
            continue

        try:
            content = extract_text(path)
        except Exception as error:
            print(f"Could not read {path.name}: {error}")
            continue

        for line_number, line in enumerate(
            content.splitlines(), start=1
        ):
            text = line.strip()

            if not text:
                continue

            line_words = set(
                re.findall(r"[a-z0-9]+", text.casefold())
            )

            matched_keywords = keywords.intersection(line_words)

            if matched_keywords:
                matches.append({
                    "filename": path.name,
                    "line_number": line_number,
                    "text": text,
                    "matched_keywords": sorted(matched_keywords),
                    "match_count": len(matched_keywords)
                })

    matches.sort(
        key=lambda item: item["match_count"],
        reverse=True
    )

    return matches[:top_k]


def retrieve_semantically(question, top_k=5):
    """Retrieve passages using ChromaDB."""

    return vector_store.search_similar_documents(
        query=question,
        n_results=top_k
    )


def build_keyword_context(results):
    """Prepare keyword search results for Claude."""

    return "\n\n".join(
        f"Source: {item['filename']}\n"
        f"Line: {item['line_number']}\n"
        f"Content: {item['text']}"
        for item in results
    )


def build_semantic_context(results):
    """Prepare semantic search results for Claude."""

    return "\n\n".join(
        f"Source: {item['filename']}\n"
        f"Chunk: {item['chunk_index']}\n"
        f"Content: {item['text']}"
        for item in results
    )


def run_comparison():
    report = []

    for question in QUESTIONS:
        print("\n" + "=" * 75)
        print("QUESTION:", question)
        print("=" * 75)

        question_result = {"question": question}

        # APPROACH A: Keyword search only
        start = time.perf_counter()
        keyword_results = retrieve_by_keywords(question)
        keyword_retrieval_time = time.perf_counter() - start

        print("\n[A] KEYWORD SEARCH ONLY")
        print("Retrieval time:", round(keyword_retrieval_time, 4), "seconds")

        for item in keyword_results:
            print(
                item["filename"],
                "| Matches:", item["match_count"],
                "|", item["text"][:180]
            )

        question_result["keyword_only"] = {
            "retrieval_time_seconds": round(
                keyword_retrieval_time, 4
            ),
            "results": keyword_results
        }

        # APPROACH B: Keyword search + Claude
        print("\n[B] KEYWORD SEARCH + CLAUDE")

        start = time.perf_counter()
        keyword_context = build_keyword_context(keyword_results)

        if keyword_context:
            answer_b = claude_client.generate_answer(
                question=question,
                context=keyword_context
            )
        else:
            answer_b = "No relevant keyword matches found."

        claude_keyword_time = time.perf_counter() - start

        print("Claude generation time:", round(
            claude_keyword_time, 4
        ), "seconds")
        print("Answer:", answer_b)

        question_result["keyword_claude"] = {
            "answer": answer_b,
            "claude_time_seconds": round(
                claude_keyword_time, 4
            ),
            "sources": [
                {
                    "filename": item["filename"],
                    "line_number": item["line_number"]
                }
                for item in keyword_results
            ]
        }

        # APPROACH C: Semantic search + Claude
        print("\n[C] SEMANTIC SEARCH + CLAUDE")

        start = time.perf_counter()
        semantic_results = retrieve_semantically(question)
        semantic_retrieval_time = time.perf_counter() - start

        semantic_context = build_semantic_context(semantic_results)

        start = time.perf_counter()

        if semantic_context:
            answer_c = claude_client.generate_answer(
                question=question,
                context=semantic_context
            )
        else:
            answer_c = "No relevant semantic matches found."

        claude_semantic_time = time.perf_counter() - start

        print("Semantic retrieval time:", round(
            semantic_retrieval_time, 4
        ), "seconds")
        print("Claude generation time:", round(
            claude_semantic_time, 4
        ), "seconds")
        print("Answer:", answer_c)

        question_result["semantic_claude"] = {
            "retrieval_time_seconds": round(
                semantic_retrieval_time, 4
            ),
            "claude_time_seconds": round(
                claude_semantic_time, 4
            ),
            "answer": answer_c,
            "sources": [
                {
                    "filename": item["filename"],
                    "chunk_index": item["chunk_index"],
                    "distance": round(item["distance"], 4)
                }
                for item in semantic_results
            ]
        }

        report.append(question_result)

    # Save all results
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print("\n" + "=" * 75)
    print("COMPARISON COMPLETED")
    print("Report saved to:", REPORT_PATH)
    print("=" * 75)


if __name__ == "__main__":
    run_comparison()

