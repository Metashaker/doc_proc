import os
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks, HTTPException

from app.config import settings
from app.models import Document, ProcessingStatus
from app.services.pdf_processor import extract_text_from_pdf
from app.services.storage import save_upload


async def _parse_document(document_id: int, file_path: str) -> None:
    from app.database import async_session

    async with async_session() as session:
        await _parse_document_with_session(document_id, file_path, session)


async def _parse_document_with_session(
    document_id: int,
    file_path: str,
    db: AsyncSession,
) -> None:
    try:
        text_content, page_count = await extract_text_from_pdf(file_path)
    except ValueError:
        status = await db.get(ProcessingStatus, document_id)
        if status:
            status.status = "failed"
            status.error_message = "Invalid or corrupted PDF"
            status.processed_at = datetime.utcnow()
            await db.commit()
        if os.path.exists(file_path):
            os.remove(file_path)
        return

    document = await db.get(Document, document_id)
    if document:
        document.content = text_content
        document.page_count = page_count
        await db.commit()

    status = await db.get(ProcessingStatus, document_id)
    if status:
        status.status = "completed"
        status.processed_at = datetime.utcnow()
        await db.commit()

    if os.path.exists(file_path):
        os.remove(file_path)


async def create_document(file, db: AsyncSession, background_tasks: BackgroundTasks | None = None) -> Document:
    file_path, file_size, original_name = await save_upload(
        file,
        settings.UPLOAD_DIR,
        settings.MAX_UPLOAD_BYTES,
    )

    document = Document(
        filename=original_name,
        file_size=file_size,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    processing_status = ProcessingStatus(
        document_id=document.id,
        status="processing",
    )
    db.add(processing_status)
    await db.commit()

    if background_tasks is None:
        background_tasks = BackgroundTasks()
    background_tasks.add_task(_parse_document, document.id, file_path)

    return document
