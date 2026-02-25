import time
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL
from agent.searcher   import search_web, fetch_text
from agent.processor  import build_docs, embed_and_rank
from agent.summarizer import summarize


class ResearchAgent:
    def __init__(self):
        # Load model once at startup — this downloads it on first run (~80 MB)
        print(f"Loading embedding model: {EMBEDDING_MODEL}")
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        print("Model loaded. Ready.\n")

    def run(self, query):
        start = time.time()

        # ── Step 1: Search ───────────────────────────────
        print(f"Searching for: {query}")
        urls = search_web(query)
        print(f"Found {len(urls)} URLs.")

        # ── Step 2: Fetch and chunk ──────────────────────
        print("Fetching pages...")
        docs = build_docs(urls, fetch_text)
        print(f"Built {len(docs)} passages.")

        if not docs:
            return {"query": query, "passages": [], "summary": "Nothing found."}

        # ── Step 3: Embed and rank ───────────────────────
        print("Embedding and ranking...")
        top_passages = embed_and_rank(query, docs, self.embedder)

        # ── Step 4: Summarize ────────────────────────────
        query_emb = self.embedder.encode([query], convert_to_numpy=True)[0]
        summary   = summarize(query_emb, top_passages, self.embedder)

        return {
            "query":    query,
            "passages": top_passages,
            "summary":  summary,
            "time":     round(time.time() - start, 1)
        }


if __name__ == "__main__":
    agent = ResearchAgent()

    query  = "What causes urban heat islands and how can cities reduce them?"
    result = agent.run(query)

    print("\n=== TOP PASSAGES ===")
    for p in result["passages"]:
        print(f"\nScore: {p['score']:.3f}  |  {p['url']}")
        print(f"  {p['passage'][:200]}...")

    print("\n=== SUMMARY ===")
    print(result["summary"])
    print(f"\nCompleted in {result['time']}s")
