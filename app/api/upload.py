from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.blob_service import upload_to_blob
from app.services.extractor import extract_text_from_upload
from app.services.search_index import index_document_item
import uuid

router = APIRouter()

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    # Save file to blob
    blob_name = f"{uuid.uuid4()}_{file.filename}"
    blob_url = upload_to_blob(file, blob_name)
    # Extract text
    text = await extract_text_from_upload(file)
    # Index into Cognitive Search (embedding & vector stored)
    doc_id = blob_name
    metadata = {"filename": file.filename, "blob_url": blob_url}
    await index_document_item(doc_id=doc_id, content=text, metadata=metadata)
    return {"status": "ok", "doc_id": doc_id, "blob_url": blob_url}
