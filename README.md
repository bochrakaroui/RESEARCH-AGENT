# Research Agent

A fully local, privacy-preserving AI research assistant that searches the web, retrieves semantically relevant passages, and synthesises grounded answers using a local language model — no paid APIs, no data leaving your machine.

---

## Overview

Research Agent is a Retrieval-Augmented Generation (RAG) pipeline built from scratch. Given a natural-language question, it:

1. **Searches** the web via DuckDuckGo (no API key required)
2. **Fetches and scrapes** the top result pages
3. **Chunks and embeds** the content using a sentence-transformer model
4. **Stores** passage vectors persistently in ChromaDB
5. **Retrieves** the most semantically relevant passages for the query
6. **Generates** a fluent, cited answer using a local Ollama LLM
7. **Presents** the result through a clean Streamlit chat interface

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Streamlit Frontend                  │
│                     app.py                          │
│         Chat UI · Session state · REST calls        │
└───────────────────┬─────────────────────────────────┘
                    │ HTTP POST /research
                    ▼
┌─────────────────────────────────────────────────────┐
│                  FastAPI Backend                     │
│                     api.py                          │
│           REST endpoints · Request routing          │
└──────┬────────────────┬───────────────┬─────────────┘
       │                │               │
       ▼                ▼               ▼
┌────────────┐  ┌──────────────┐  ┌──────────────────┐
│  Searcher  │  │  Processor   │  │    Generator     │
│searcher.py │  │processor.py  │  │  generator.py    │
│            │  │              │  │                  │
│ DuckDuckGo │  │ Chunk · Embed│  │  Ollama LLM      │
│ requests   │  │ Rank · Score │  │  llama3.2        │
│ BeautifulS.│  │ sentence-    │  │                  │
└────────────┘  │ transformers │  └──────────────────┘
                └──────┬───────┘
                       │
                       ▼
              ┌─────────────────┐
              │    ChromaDB     │
              │    store.py     │
              │                 │
              │ Persistent      │
              │ vector store    │
              │ ./chroma_store/ │
              └─────────────────┘
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Streamlit | Chat interface |
| Backend | FastAPI + Uvicorn | REST API server |
| Search | ddgs (DuckDuckGo) | Free web search |
| Scraping | requests + BeautifulSoup4 | HTML parsing |
| Embeddings | sentence-transformers | Text vectorisation |
| Vector store | ChromaDB | Persistent passage index |
| LLM | Ollama (llama3.2) | Answer generation |
| Language | Python 3.10+ | — |

---

## Project Structure

```
AI-agent-to-automate-research/
│
├── agent/
│   ├── __init__.py          # Package marker
│   ├── searcher.py          # Web search + HTML fetching
│   ├── processor.py         # Chunking, embedding, ranking
│   ├── generator.py         # Ollama LLM answer generation
│   └── store.py             # ChromaDB read / write
│
├── chroma_store/            # Auto-created — persistent vector index
│
├── config.py                # All constants and settings
├── main.py                  # ResearchAgent class + CLI entry point
├── api.py                   # FastAPI server and endpoint definitions
├── app.py                   # Streamlit frontend
└── requirements.txt         # Python dependencies
```

---

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10 or higher** — [python.org](https://www.python.org/downloads/)
- **Git** — [git-scm.com](https://git-scm.com/)
- **Ollama** — [ollama.com/download](https://ollama.com/download)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/AI-agent-to-automate-research.git
cd AI-agent-to-automate-research
```

### 2. Create and activate a virtual environment

```bash
# Create
python -m venv venv

# Activate — macOS / Linux
source venv/bin/activate

# Activate — Windows
venv\Scripts\activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Pull the Ollama model

Make sure Ollama is running , then pull the model:

```bash
ollama pull llama3.2
```

---

## Configuration

All settings are centralised in `config.py`. Edit this file to tune the agent's behaviour:

```python
# Search
SEARCH_RESULTS    = 6      # Number of URLs to fetch per query
PASSAGES_PER_PAGE = 4      # Max text chunks extracted per URL
TIMEOUT           = 8      # HTTP request timeout (seconds)

# Embeddings & retrieval
EMBEDDING_MODEL   = "sentence-transformers/all-mpnet-base-v2"
TOP_PASSAGES      = 5      # Passages sent to the LLM as context

# Generation
OLLAMA_MODEL      = "llama3.2"

# Storage
CHROMA_PATH       = "./chroma_store"
CHROMA_COLLECTION = "research"
```


---

## Running the Project

You need **three things running simultaneously**. Open separate terminal windows for each.

### Window 1 — Verify Ollama is running

On Windows, check the system tray for the Ollama icon. If it is not there:

```bash
ollama serve
```

### Window 2 — Start the FastAPI backend

```bash
# Activate venv first
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

uvicorn api:app --reload --port 8000
```

Wait for:
```
INFO:     Application startup complete.
```

### Window 3 — Start the Streamlit frontend

```bash
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

streamlit run app.py
```

Your browser will open automatically at **http://localhost:8501**.

---



## Acknowledgements

- [DuckDuckGo Search](https://github.com/deedy5/duckduckgo_search) — free search without API keys
- [Sentence Transformers](https://www.sbert.net/) — semantic embedding models
- [ChromaDB](https://www.trychroma.com/) — local vector database
- [Ollama](https://ollama.com/) — local LLM inference
- [FastAPI](https://fastapi.tiangolo.com/) — modern Python web framework
- [Streamlit](https://streamlit.io/) — rapid Python UI development