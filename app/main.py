from fastapi import FastAPI
from app.api import upload, query

app = FastAPI(title="RAG - FastAPI + Azure Cognitive Search")

app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(query.router, prefix="/query", tags=["query"])

@app.get("/")
async def health():
    return {"status": "ok"}
