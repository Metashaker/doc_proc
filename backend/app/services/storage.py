import os
from uuid import uuid4

from fastapi import HTTPException, UploadFile


ALLOWED_CONTENT_TYPES = {"application/pdf"}
ALLOWED_EXTENSIONS = {".pdf"}


def sanitize_filename(filename: str | None) -> str:
    if not filename:
        return "upload.pdf"
    return os.path.basename(filename)


def _validate_upload(file: UploadFile) -> str:
    original_name = sanitize_filename(file.filename)
    ext = os.path.splitext(original_name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid content type")
    return original_name


async def save_upload(
    file: UploadFile,
    upload_dir: str,
    max_bytes: int,
    chunk_size: int = 1024 * 1024,
) -> tuple[str, int, str]:
    original_name = _validate_upload(file)
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(original_name)[1].lower()
    stored_name = f"{uuid4().hex}{ext}"
    file_path = os.path.join(upload_dir, stored_name)

    size = 0
    try:
        with open(file_path, "wb") as output:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                size += len(chunk)
                if size > max_bytes:
                    raise HTTPException(status_code=413, detail="File too large")
                output.write(chunk)
    except HTTPException:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise
    finally:
        await file.close()

    if size == 0:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail="Empty file upload")

    return file_path, size, original_name
