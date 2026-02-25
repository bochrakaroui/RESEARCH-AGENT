import re
import numpy as np
from config import SUMMARY_SENTENCES

def split_sentences(text):
    """
    Split a passage into individual sentences using punctuation.
    Returns a list of non-empty sentence strings.
    """
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p.strip() for p in parts if p.strip()]

def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10)

def summarize(query_emb, top_passages, embedder):
    """
    Build an extractive summary from the top-ranked passages.

    Steps:
    1. Split every passage into individual sentences.
    2. Embed all sentences.
    3. Rank sentences by similarity to the query embedding.
    4. De-duplicate and return the top SUMMARY_SENTENCES.
    """
    # Collect every sentence with its source URL
    sentences = []
    for tp in top_passages:
        for s in split_sentences(tp["passage"]):
            sentences.append({"sent": s, "url": tp["url"]})

    if not sentences:
        return "No summary could be generated."

    # Embed all sentences in one batch
    sent_embs = embedder.encode(
        [s["sent"] for s in sentences],
        convert_to_numpy=True,
        show_progress_bar=False
    )

    # Rank sentences by similarity to the query
    sims    = [cosine(e, query_emb) for e in sent_embs]
    top_idx = np.argsort(sims)[::-1][:SUMMARY_SENTENCES]

    # De-duplicate using the first 80 characters as a fingerprint
    seen, lines = set(), []
    for i in top_idx:
        key = sentences[i]["sent"].lower()[:80]
        if key not in seen:
            seen.add(key)
            lines.append(
                f"{sentences[i]['sent']} (Source: {sentences[i]['url']})"
            )

    return " ".join(lines)
