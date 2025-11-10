import os
import json
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, ComplexField, SearchFieldDataType, VectorSearch, VectorSearchAlgorithmConfiguration
)
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.openai import OpenAIClient
import asyncio

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX", "documents-index")
OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
EMBED_MODEL = os.getenv("AZURE_OPENAI_EMBED_MODEL", "text-embedding-3-small")
# Set expected embedding dimension: adjust if model differs
EMBED_DIM = 1536

# Create Search Index (call once)
def create_search_index():
    admin_client = SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=AzureKeyCredential(SEARCH_KEY))

    vector_search = VectorSearch(
        algorithm_configurations=[
            VectorSearchAlgorithmConfiguration(name="cosine", kind="cosine")
        ]
    )

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String, analyzer_name="en.lucene"),
        SimpleField(name="filename", type=SearchFieldDataType.String, filterable=True, facetable=False),
        SimpleField(name="blob_url", type=SearchFieldDataType.String, filterable=False),
        SimpleField(name="metadata", type=SearchFieldDataType.String, filterable=False),
        # vector field: collection of floats
        SearchableField(name="content_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single))
    ]

    index = SearchIndex(name=INDEX_NAME, fields=fields, vector_search=vector_search)
    try:
        admin_client.create_index(index)
        print("Index created:", INDEX_NAME)
    except Exception as e:
        print("Index creation error (maybe exists):", e)

# helper to embed text via Azure OpenAI
def get_embedding(text: str):
    client = OpenAIClient(OPENAI_ENDPOINT, credential=AzureKeyCredential(OPENAI_KEY))
    resp = client.embeddings.create(model=EMBED_MODEL, input=text)
    # returns a list of floats
    return resp.data[0].embedding

# Index a single doc (id, content, metadata)
async def index_document_item(doc_id: str, content: str, metadata: dict):
    # break into chunks for better retrieval (simple split)
    CHUNK_SIZE = 800
    chunks = []
    for i in range(0, len(content), CHUNK_SIZE):
        chunk_text = content[i:i+CHUNK_SIZE]
        chunks.append(chunk_text)

    search_client = SearchClient(endpoint=SEARCH_ENDPOINT, index_name=INDEX_NAME, credential=AzureKeyCredential(SEARCH_KEY))
    actions = []
    for idx, chunk in enumerate(chunks):
        emb = get_embedding(chunk)
        doc = {
            "id": f"{doc_id}_{idx}",
            "content": chunk,
            "filename": metadata.get("filename"),
            "blob_url": metadata.get("blob_url"),
            "metadata": json.dumps({k:v for k,v in metadata.items()})
        }
        # azure search expects vector field name equal to what you created; here we used 'content_vector'
        doc["content_vector"] = emb
        actions.append(doc)

    # upload in one call
    try:
        result = search_client.upload_documents(documents=actions)
        return result
    except Exception as e:
        print("Indexing error:", e)
        raise
