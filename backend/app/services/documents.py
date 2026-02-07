import os
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.config import settings
from app.models import Document, ProcessingStatus
from app.services.pdf_processor import extract_text_from_pdf
from app.services.storage import save_upload


async def create_document(file, db: AsyncSession) -> Document:
    file_path, file_size, original_name = await save_upload(
        file,
        settings.UPLOAD_DIR,
        settings.MAX_UPLOAD_BYTES,
    )

    try:
        text_content, page_count = await extract_text_from_pdf(file_path)
    except ValueError as exc:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    document = Document(
        filename=original_name,
        content=text_content,
        file_size=file_size,
        page_count=page_count,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    processing_status = ProcessingStatus(
        document_id=document.id,
        status="completed",
        processed_at=datetime.utcnow(),
    )
    db.add(processing_status)
    await db.commit()

    return document
