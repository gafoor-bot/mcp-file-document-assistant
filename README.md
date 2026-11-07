# 🚀 MCP File & Document Assistant

### An AI-powered document assistant built with Python, Model Context Protocol (MCP), ChromaDB, and Claude AI.

Search, retrieve, and ask questions about PDF and text documents using keyword search and Retrieval-Augmented Generation (RAG).

---

## 📌 Overview

The **MCP File & Document Assistant** is a Python-based application that allows AI assistants to interact with local documents through the Model Context Protocol (MCP).

It combines document processing, vector embeddings, semantic search, and Large Language Models (LLMs) to retrieve relevant information and generate context-aware answers.

The project explores three document retrieval approaches:

1. **Keyword Search** – Finds document passages using matching keywords.
2. **Keyword Search + Claude** – Retrieves matching passages and uses Claude to generate answers.
3. **Semantic Search + Claude** – Uses vector embeddings and ChromaDB to retrieve contextually relevant passages before generating answers with Claude.

## ✨ Key Features

- 📄 **PDF & TXT Processing** – Extract content from PDF and text documents.
- 🔍 **Keyword Search** – Search documents using matching words.
- 🧠 **Semantic Search** – Find relevant information based on meaning.
- 🤖 **Claude AI Integration** – Generate natural-language answers using document context.
- 🗂️ **Document Indexing** – Process, chunk, and index documents.
- 📊 **Vector Database** – Store and retrieve embeddings using ChromaDB.
- 🔌 **MCP Integration** – Expose document operations as MCP tools.
- 🧪 **Search Comparison** – Evaluate keyword search, keyword + Claude, and semantic + Claude.

## 🏗️ Architecture

```text
                 User / AI Assistant
                         |
                         v
                   MCP Inspector
                         |
                         v
                  Python MCP Server
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
     File Search    Document Read   Document Create
          |
          v
    Document Processing
          |
          v
    PDF / TXT Extraction
          |
          v
      Text Chunking
          |
          v
   Sentence Transformers
          |
          v
       Embeddings
          |
          v
       ChromaDB
          |
          v
    Semantic Retrieval
          |
          v
       Claude API
          |
          v
   Contextual AI Answers
```

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Backend development |
| Model Context Protocol | AI-to-tool communication |
| MCP Python SDK | MCP server implementation |
| Anthropic Claude API | AI-generated answers |
| ChromaDB | Vector database |
| Sentence Transformers | Embedding generation |
| PyMuPDF | PDF text extraction |
| SQLite | Document metadata storage |
| Pytest | Unit testing |
| dotenv | Environment configuration |

## 📂 Project Structure

```text
mcp-file-assistant/
│
├── server.py
├── database.py
├── claude_client.py
├── vector_store.py
├── test_claude.py
├── test_vector_store.py
├── compare_search.py
│
├── tests/
│   └── test_file_operations.py
│
├── data/
│   ├── documents/
│   ├── database/
│   └── vector_db/
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

*Note: Local documents, databases, and vector storage should remain excluded from the public repository.*

## ⚙️ Getting Started

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd mcp-file-assistant
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it:

**macOS / Linux**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root.

```env
ANTHROPIC_API_KEY=your_anthropic_api_key
```

Never commit `.env` or expose API credentials in GitHub.

### 5. Add documents

Place supported PDF and TXT files inside:

```text
data/documents/
```

### 6. Index documents and test semantic search

```bash
python test_vector_store.py
```

This extracts document content, creates chunks, generates embeddings, and stores them in ChromaDB before running the semantic search tests.

### 7. Run the MCP server

```bash
./.venv/bin/mcp dev server.py
```

Open MCP Inspector and connect to the server to test the available tools.

## 🔎 Search Approaches

### Approach 1: Keyword Search

Uses text matching to find passages containing relevant keywords.

### Approach 2: Keyword Search + Claude

Retrieves keyword-matched passages and sends them to Claude for answer generation.

### Approach 3: Semantic Search + Claude

Generates embeddings for questions, searches ChromaDB for semantically relevant passages, and sends retrieved context to Claude.

## 📊 Experiment Results

The initial five-question experiment demonstrated:

| Evaluation | Keyword Search | Keyword + Claude | Semantic + Claude |
|---|---|---|---|
| Amazon revenue | Relevant passage | Correct answer | Correct answer |
| Amazon segments | Relevant passage | Correct answer | Correct answer |
| Amazon risks | Poor retrieval | Insufficient context | Partial context |
| Programming languages | Irrelevant matches | Could not answer | Correct answer |
| Paid time off | Correct passage | Correct answer | Correct answer |

**Initial observation:** Semantic retrieval performed better on questions requiring contextual understanding, while keyword search provided a useful baseline.

These are qualitative results from an initial experiment, not a statistically validated benchmark.

## 🧪 Testing

Run unit tests:

```bash
pytest -v
```

Run semantic search tests:

```bash
python test_vector_store.py
```

Run the three-way search comparison:

```bash
python compare_search.py
```

The comparison script generates `comparison_results.json` containing experiment answers, source information, and timing measurements.

## 🔐 Security Considerations

- Keep API keys in environment variables.
- Never commit `.env` files.
- Exclude private documents and personal information.
- Exclude local databases and vector storage.
- Validate document paths before performing file operations.
- Apply authentication and authorization before exposing tools remotely.

## 🚀 Future Enhancements

- [ ] Incremental document indexing
- [ ] Automatic detection of modified documents
- [ ] Advanced document chunking
- [ ] PDF page-level source references
- [ ] Retrieval reranking
- [ ] Hybrid keyword and semantic search
- [ ] Remote MCP deployment using Streamable HTTP
- [ ] Authentication and access control
- [ ] Docker containerization
- [ ] Cloud deployment on AWS
- [ ] Improved evaluation metrics and automated RAG testing

## 🎯 Learning Objectives

This project demonstrates practical experience with:

- Building MCP servers using Python.
- Integrating AI models with external tools.
- Designing Retrieval-Augmented Generation workflows.
- Implementing vector-based semantic search.
- Processing and indexing enterprise documents.
- Integrating LLM APIs.
- Testing and evaluating retrieval strategies.

## 👨‍💻 Author

**Gafoor Shaik**

MCP | Python | Backend Development | AI Integration | RAG | AWS

---

⭐ If you find this project interesting, feel free to explore and contribute!

