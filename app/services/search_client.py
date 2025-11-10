import os
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.openai import OpenAIClient
import json
from typing import List

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX", "documents-index")
OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
EMBED_MODEL = os.getenv("AZURE_OPENAI_EMBED_MODEL", "text-embedding-3-small")
CHAT_DEPLOY = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")

search_client = SearchClient(endpoint=SEARCH_ENDPOINT, index_name=INDEX_NAME, credential=AzureKeyCredential(SEARCH_KEY))
openai_client = OpenAIClient(OPENAI_ENDPOINT, AzureKeyCredential(OPENAI_KEY))

def embed_text(text: str) -> List[float]:
    resp = openai_client.embeddings.create(model=EMBED_MODEL, input=text)
    return resp.data[0].embedding

async def semantic_query_and_generate(query: str, top_k: int = 3):
    # 1) get embedding of query
    q_emb = embed_text(query)
    # 2) vector search using Azure Cognitive Search vector search feature
    # The 'vector' argument format is available in azure.search.documents.search_client.search
    results = search_client.search(
        search_text=None,
        vector={"value": q_emb, "fields": "content_vector", "k": top_k},
        top=top_k
    )

    contexts = []
    for r in results:
        # each r is a SearchResult with .get
        content = r.get("content", "")
        filename = r.get("filename")
        blob_url = r.get("blob_url")
        contexts.append(f"{content}\n--source: {filename} {blob_url}")

    context_block = "\n\n---\n\n".join(contexts)

    # 3) call OpenAI / Chat completion with context
    prompt = f"""You are an assistant that answers using only the context provided. If the answer is not in the context, say you don't know.

Context:
{context_block}

Question:
{query}

Answer concisely and cite sources when possible (give filename or blob_url).
"""

    # call Azure OpenAI ChatCompletions via azure.ai.openai Chat API
    chat_resp = openai_client.chat.completions.create(
        deployment_id=CHAT_DEPLOY,
        messages=[
            {"role":"system","content":"You are a helpful assistant."},
            {"role":"user","content":prompt}
        ],
        max_tokens=512,
        temperature=0.2
    )

    # get the assistant message
    return chat_resp.choices[0].message.content
