from fastapi import APIRouter, Depends, UploadFile, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Document, ProcessingStatus
from app.schemas import DocumentResponse, DocumentDetail
from app.services.documents import create_document

router = APIRouter()


@router.post("/documents")
async def upload_document(file: UploadFile, db: AsyncSession = Depends(get_db)):
    document = await create_document(file, db)
    return {"id": document.id, "filename": document.filename}


@router.get("/documents")
async def list_documents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document))
    documents = result.scalars().all()

    response = []
    for doc in documents:
        status_result = await db.execute(
            select(ProcessingStatus).where(ProcessingStatus.document_id == doc.id)
        )
        status = status_result.scalar_one_or_none()
        response.append(
            DocumentResponse(
                id=doc.id,
                filename=doc.filename,
                file_size=doc.file_size,
                page_count=doc.page_count,
                status=status.status if status else "unknown",
                created_at=doc.created_at,
            )
        )

    return response


@router.get("/documents/{document_id}")
async def get_document(document_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    status_result = await db.execute(
        select(ProcessingStatus).where(ProcessingStatus.document_id == document.id)
    )
    status = status_result.scalar_one_or_none()

    return DocumentDetail(
        id=document.id,
        filename=document.filename,
        content=document.content,
        file_size=document.file_size,
        page_count=document.page_count,
        status=status.status if status else "unknown",
        created_at=document.created_at,
    )


@router.delete("/documents/{document_id}")
async def delete_document(document_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    status_result = await db.execute(
        select(ProcessingStatus).where(ProcessingStatus.document_id == document.id)
    )
    status = status_result.scalar_one_or_none()
    if status:
        await db.delete(status)

    await db.delete(document)
    await db.commit()

    return {"message": "Document deleted"}
