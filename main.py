import time
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL, TOP_PASSAGES , RETRIEVAL_CANDIDATE
from agent.searcher  import search_web, fetch_text
from agent.processor import build_docs, chunk_passages, cosine , embed_and_rank
from agent.generator import generate_answer
from agent.store     import get_collection, is_indexed, add_passages, query_collection
class ResearchAgent:
    def __init__(self):
        print(f"Loading embedding model: {EMBEDDING_MODEL}")
        self.embedder   = SentenceTransformer(EMBEDDING_MODEL)
        #opens or creates the ChromaDB collection 
        self.collection = get_collection()
        print("Ready.\n")

    def run(self, query):
        start = time.time()

        print(f"Searching for: {query}")
        urls = search_web(query)
        print(f"Found {len(urls)} URLs.")

        new_docs = []
        for url in urls:
            if is_indexed(self.collection, url):
                print(f"  [cached]  {url}")
                continue
            print(f"  [fetching] {url}")
            text = fetch_text(url)
            if not text:
                continue
            from config import PASSAGES_PER_PAGE
            for chunk in chunk_passages(text)[:PASSAGES_PER_PAGE]:
                new_docs.append({"url": url, "passage": chunk})

        # Embed and store new passages
        if new_docs:
            print(f"Indexing {len(new_docs)} new passages into ChromaDB...")
            texts = [d["passage"] for d in new_docs]
            embs  = self.embedder.encode(texts, convert_to_numpy=True,
                                          show_progress_bar=False)
            add_passages(self.collection, new_docs, embs)

        #  Query ChromaDB for the best passages 
        print("Querying vector store...")
        query_emb    = self.embedder.encode([query], convert_to_numpy=True)[0]
        top_passages = query_collection(self.collection, query_emb,
                                        n_results=RETRIEVAL_CANDIDATE)
        top_passages = embed_and_rank(query, top_passages, self.embedder)[:TOP_PASSAGES]

        if not top_passages:
            return {"query": query, "passages": [], "answer": "Nothing found."}

        #  Generate answer with Ollama 
        print("Generating answer with Ollama (this may take ~10-20s)...")
        answer = generate_answer(query, top_passages)

        return {
            "query":    query,
            "passages": top_passages,
            "answer":   answer,
            "time":     round(time.time() - start, 1)
        }


if __name__ == "__main__":
    agent  = ResearchAgent()
    query  = "What causes urban heat islands and how can cities reduce them?"
    result = agent.run(query)

    print("\n=== TOP PASSAGES ===")
    for p in result["passages"]:
        print(f"\nScore: {p['score']:.4f}  |  {p['url']}")
        print(f"  {p['passage'][:200]}...")

    print("\n=== GENERATED ANSWER ===")
    print(result["answer"])
    print(f"\nCompleted in {result['time']}s")
