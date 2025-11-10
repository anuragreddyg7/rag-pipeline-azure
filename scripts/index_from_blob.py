import os
from azure.storage.blob import BlobServiceClient
from app.services.extractor import extract_text_from_upload
from app.services.search_index import index_document_item
from azure.core.exceptions import ResourceNotFoundError
from io import BytesIO

CONN_STR = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER = os.getenv("AZURE_BLOB_CONTAINER", "documents")

blob_service = BlobServiceClient.from_connection_string(CONN_STR)
container_client = blob_service.get_container_client(CONTAINER)

def run():
    blobs = container_client.list_blobs()
    for b in blobs:
        name = b.name
        print("Indexing", name)
        blob_client = container_client.get_blob_client(name)
        stream = blob_client.download_blob().readall()
        bio = BytesIO(stream)
        # naive filename extraction
        text = extract_text_from_upload.__wrapped__(type("F",(object,),{"file":bio,"filename":name}))  # hack: reuse function
        metadata = {"filename": name, "blob_url": blob_client.url}
        import asyncio
        asyncio.run(index_document_item(doc_id=name, content=text, metadata=metadata))

if __name__ == "__main__":
    run()
