
import vector_store

# Step 1: Index all documents, including new PDFs
print("\nStarting document indexing...")

index_result = vector_store.index_documents()

print("\nIndexing completed!")
print("Files indexed:", index_result["indexed_files"])
print("Total chunks:", index_result["total_chunks"])

# Step 2: Run semantic search questions
questions = [
    "Tell me about my backend development experience",
    "What programming languages do I know?",
    "How much paid time off do employees receive?",
    "What was Amazon's total revenue in 2025?",
    "What are Amazon's major business segments?",
    "What risks does Amazon identify in its annual report?"
]

for question in questions:
    print("\n" + "=" * 60)
    print("Question:", question)

    results = vector_store.search_similar_documents(
        question,
        n_results=3
    )

    for result in results:
        print("\nSource:", result["filename"])
        print("Chunk:", result["chunk_index"])
        print("Distance:", round(result["distance"], 4))
        print("Content:", result["text"][:500])
