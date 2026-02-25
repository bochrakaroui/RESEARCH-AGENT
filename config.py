CHUNK_SIZE    = 120   # words per chunk
CHUNK_OVERLAP = 30    # words shared between consecutive chunks
# number of URLs to fetch from DuckDuckGo
SEARCH_RESULTS    = 3

# number of passages to keep per URL
PASSAGES_PER_PAGE = 4

# The embedding model to use.
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"

# number of top-ranked passages to use for the summary
TOP_PASSAGES      = 5
RETRIEVAL_CANDIDATE = 15   # how many to fetch from ChromaDB before re-ranking

# number of sentences to include in the final summary
SUMMARY_SENTENCES = 3

# Seconds to wait before giving up on a slow URL
TIMEOUT           = 8

# Ollama settings
OLLAMA_MODEL = "llama3.2"

# ChromaDB settings
CHROMA_PATH       = "./chroma_store"
CHROMA_COLLECTION = "research"