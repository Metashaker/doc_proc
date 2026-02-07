import io
import os
import sys

import pytest
from fastapi import HTTPException
from starlette.datastructures import UploadFile, Headers

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.storage import save_upload


@pytest.mark.asyncio
async def test_save_upload_rejects_non_pdf_extension(tmp_path):
    upload = UploadFile(
        filename="notes.txt",
        file=io.BytesIO(b"data"),
        headers=Headers({"content-type": "text/plain"}),
    )
    with pytest.raises(HTTPException):
        await save_upload(upload, str(tmp_path), max_bytes=10)


@pytest.mark.asyncio
async def test_save_upload_rejects_invalid_content_type(tmp_path):
    upload = UploadFile(
        filename="notes.pdf",
        file=io.BytesIO(b"data"),
        headers=Headers({"content-type": "text/plain"}),
    )
    with pytest.raises(HTTPException):
        await save_upload(upload, str(tmp_path), max_bytes=10)


@pytest.mark.asyncio
async def test_save_upload_enforces_size_limit(tmp_path):
    upload = UploadFile(
        filename="big.pdf",
        file=io.BytesIO(b"x" * 20),
        headers=Headers({"content-type": "application/pdf"}),
    )
    with pytest.raises(HTTPException) as excinfo:
        await save_upload(upload, str(tmp_path), max_bytes=10, chunk_size=4)
    assert excinfo.value.status_code == 413
    assert not any(tmp_path.iterdir())


@pytest.mark.asyncio
async def test_save_upload_success(tmp_path):
    upload = UploadFile(
        filename="ok.pdf",
        file=io.BytesIO(b"content"),
        headers=Headers({"content-type": "application/pdf"}),
    )
    file_path, size, original = await save_upload(upload, str(tmp_path), max_bytes=1024)
    assert original == "ok.pdf"
    assert size == 7
    assert tmp_path.joinpath(file_path.split("/")[-1]).exists()


@pytest.mark.asyncio
async def test_save_upload_rejects_empty_file(tmp_path):
    upload = UploadFile(
        filename="empty.pdf",
        file=io.BytesIO(b""),
        headers=Headers({"content-type": "application/pdf"}),
    )
    with pytest.raises(HTTPException) as excinfo:
        await save_upload(upload, str(tmp_path), max_bytes=1024)
    assert excinfo.value.status_code == 400
