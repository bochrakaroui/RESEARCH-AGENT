import numpy as np
from sentence_transformers import SentenceTransformer
from config import PASSAGES_PER_PAGE, TOP_PASSAGES

def chunk_passages(text, max_words=120):
    """
    Split a long string into non-overlapping word-window chunks.
    Example: 500-word article → four 120-word passages + one 20-word tail.
    """
    words = text.split()
    if not words:
        return []
    # Step through the word list in max_words increments
    return [" ".join(words[i : i + max_words])
            for i in range(0, len(words), max_words)]
def cosine(a, b):
    """
    Compute cosine similarity between two numpy vectors.
    The 1e-10 term prevents division by zero for empty vectors.
    """
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10)
def build_docs(urls, fetch_fn):
    """
    Fetch each URL, chunk the text, and return a flat list of passages.
    Each passage is a dict: { 'url': str, 'passage': str }

    fetch_fn is passed in (not imported directly) so this function
    is easy to test in isolation with a mock.
    """
    docs = []
    for url in urls:
        text = fetch_fn(url)
        if not text:
            continue
        # Keep only the first PASSAGES_PER_PAGE chunks per URL
        for chunk in chunk_passages(text)[:PASSAGES_PER_PAGE]:
            docs.append({"url": url, "passage": chunk})
    return docs

def embed_and_rank(query, docs, embedder):
    """
    Encode the query and all passages, then rank passages
    by cosine similarity to the query.

    Returns the top TOP_PASSAGES passages as a list of dicts,
    each containing: url, passage, score.
    """
    # Encode every passage in a single batch 
    texts     = [d["passage"] for d in docs]
    text_embs = embedder.encode(texts, convert_to_numpy=True,
                                show_progress_bar=False)
    # Encode the query 
    query_emb = embedder.encode([query], convert_to_numpy=True)[0]
    # Score every passage against the query
    sims    = [cosine(e, query_emb) for e in text_embs]
    # argsort returns ascending order; [::-1] reverses to descending
    top_idx = np.argsort(sims)[::-1][:TOP_PASSAGES]
    return [
        {"url": docs[i]["url"],
         "passage": docs[i]["passage"],
         "score": float(sims[i])}
        for i in top_idx
    ]
