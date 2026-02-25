import chromadb
from config import CHROMA_PATH, CHROMA_COLLECTION

def get_collection():
    """
    Connect to (or create) the persistent ChromaDB collection.
    The database is saved to ./chroma_store/ on disk so it
    survives between runs — no re-fetching needed for cached URLs.
    """
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"}
    )

def is_indexed(collection, url):
    """
    Check if a URL has already been fetched and stored.
    Returns True if at least one passage from this URL exists.
    """
    results = collection.get(where={"url": url}, limit=1)
    return len(results["ids"]) > 0

def add_passages(collection, docs, embeddings):
    """
    Save a batch of passages and their vectors to ChromaDB.
    Args:
        collection : the ChromaDB collection object
        docs       : list of { url, passage } dicts
        embeddings : numpy array of shape (len(docs), embedding_dim)
    """
    if not docs:
        return

    ids       = [f"{d['url']}::{i}" for i, d in enumerate(docs)]
    passages  = [d["passage"] for d in docs]
    metadatas = [{"url": d["url"]} for d in docs]
    vectors   = embeddings.tolist()  # ChromaDB expects plain Python lists

    collection.add(
        ids        = ids,
        documents  = passages,
        metadatas  = metadatas,
        embeddings = vectors
    )


def query_collection(collection, query_embedding, n_results=5):
    """
    Find the n most similar passages to the query vector.
    Returns results in the same shape as embed_and_rank() so
    the rest of the pipeline works without any changes.
    Each result is: { 'url': str, 'passage': str, 'score': float }
    """
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    passages = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        passages.append({
            "url":     meta["url"],
            "passage": doc,
            "score":   round(1 - dist, 4)  # distance → similarity
        })
    return passages