from app.utils.text_split import extract_text_from_file
from fastapi import UploadFile
import io

async def extract_text_from_upload(upload_file: UploadFile) -> str:
    upload_file.file.seek(0)
    content = upload_file.file.read()
    # create a BytesIO for reuse
    bio = io.BytesIO(content)
    return extract_text_from_file(bio, filename=upload_file.filename)
