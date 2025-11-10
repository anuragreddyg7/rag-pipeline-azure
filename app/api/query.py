from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from app.services.search_client import semantic_query_and_generate

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3

@router.post("/")
async def ask(q: QueryRequest):
    if not q.query:
        raise HTTPException(status_code=400, detail="Query is required")
    answer = await semantic_query_and_generate(q.query, top_k=q.top_k)
    return {"query": q.query, "answer": answer}
