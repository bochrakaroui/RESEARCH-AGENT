from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import ResearchAgent

app   = FastAPI(title="Research Agent API", version="2.0")
agent = ResearchAgent()  # loaded once when the server starts


#  Request + Response shapes 
class QueryRequest(BaseModel):
    query: str

class PassageOut(BaseModel):
    url:     str
    passage: str
    score:   float

class QueryResponse(BaseModel):
    query:    str
    passages: list[PassageOut]
    answer:   str
    time:     float


# Endpoints 
@app.get("/")
def root():
    return {"status": "ok", "message": "Research Agent API is running."}


@app.post("/research", response_model=QueryResponse)
def research(req: QueryRequest):
    """Submit a research question and get a generated answer."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    return agent.run(req.query)


@app.get("/collection/stats")
def stats():
    """How many passages are currently stored in ChromaDB."""
    from agent.store import get_collection
    return {"total_passages_indexed": get_collection().count()}


@app.delete("/collection/reset")
def reset():
    """Wipe ChromaDB and start fresh."""
    import chromadb
    from config import CHROMA_PATH, CHROMA_COLLECTION
    chromadb.PersistentClient(path=CHROMA_PATH).delete_collection(CHROMA_COLLECTION)
    return {"status": "collection reset successfully"}