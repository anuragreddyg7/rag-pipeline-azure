import os
from azure.storage.blob import BlobServiceClient

CONN_STR = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER = os.getenv("AZURE_BLOB_CONTAINER", "documents")

blob_service = BlobServiceClient.from_connection_string(CONN_STR)
container_client = blob_service.get_container_client(CONTAINER)

# Ensure container exists (idempotent)
try:
    container_client.create_container()
except Exception:
    pass

def upload_to_blob(file, blob_name: str):
    """
    file: fastapi UploadFile object
    blob_name: target name in blob container
    returns URL
    """
    blob_client = container_client.get_blob_client(blob_name)
    # file.file is a SpooledTemporaryFile / file-like
    file.file.seek(0)
    blob_client.upload_blob(file.file, overwrite=True)
    return blob_client.url
