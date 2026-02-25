# number of URLs to fetch from DuckDuckGo
SEARCH_RESULTS    = 3

# number of passages to keep per URL
PASSAGES_PER_PAGE = 4

# The embedding model to use.
# all-MiniLM-L6-v2 is fast (~80 MB) and high quality.
EMBEDDING_MODEL   = "sentence-transformers/all-MiniLM-L6-v2"

# number of top-ranked passages to use for the summary
TOP_PASSAGES      = 5

# number of sentences to include in the final summary
SUMMARY_SENTENCES = 3

# Seconds to wait before giving up on a slow URL
TIMEOUT           = 8

# Ollama settings
OLLAMA_MODEL = "llama3.2"

# ChromaDB settings
CHROMA_PATH       = "./chroma_store"
CHROMA_COLLECTION = "research"