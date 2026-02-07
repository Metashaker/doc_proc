from fastapi import APIRouter, Depends, UploadFile, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Document, Tag
from app.schemas import DocumentResponse, DocumentDetail, TagResponse, TagCreate, TagSummary
from app.services.documents import create_document

router = APIRouter()


@router.post("/documents")
async def upload_document(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    document = await create_document(file, db, background_tasks)
    return {"id": document.id, "filename": document.filename}


@router.get("/documents")
async def list_documents(tag: str | None = None, db: AsyncSession = Depends(get_db)):
    query = select(Document).options(
        selectinload(Document.processing_status),
        selectinload(Document.tags),
    )
    if tag:
        query = query.join(Document.tags).where(Tag.name == tag.lower())
    result = await db.execute(query)
    documents = result.scalars().all()

    response = []
    for doc in documents:
        status = doc.processing_status
        response.append(
            DocumentResponse(
                id=doc.id,
                filename=doc.filename,
                file_size=doc.file_size,
                page_count=doc.page_count,
                status=status.status if status else "unknown",
                created_at=doc.created_at,
                tags=[TagSummary(id=tag.id, name=tag.name) for tag in doc.tags],
            )
        )

    return response


@router.get("/documents/{document_id}")
async def get_document(document_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Document)
        .where(Document.id == document_id)
        .options(selectinload(Document.tags))
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    await db.refresh(document, attribute_names=["processing_status"])
    status = document.processing_status

    return DocumentDetail(
        id=document.id,
        filename=document.filename,
        content=document.content,
        file_size=document.file_size,
        page_count=document.page_count,
        status=status.status if status else "unknown",
        created_at=document.created_at,
        tags=[TagSummary(id=tag.id, name=tag.name) for tag in document.tags],
    )


@router.get("/tags")
async def list_tags(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag))
    return [TagResponse.model_validate(tag) for tag in result.scalars().all()]


@router.post("/documents/{document_id}/tags")
async def add_tag(document_id: int, payload: TagCreate, db: AsyncSession = Depends(get_db)):
    tag_name = payload.name.strip().lower()
    if not tag_name:
        raise HTTPException(status_code=400, detail="Tag name is required")

    document = await db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    result = await db.execute(select(Tag).where(Tag.name == tag_name))
    tag = result.scalar_one_or_none()
    if not tag:
        tag = Tag(name=tag_name)
        db.add(tag)
        await db.commit()
        await db.refresh(tag)

    await db.refresh(document, attribute_names=["tags"])
    if tag not in document.tags:
        document.tags.append(tag)
        await db.commit()

    return TagResponse.model_validate(tag)


@router.delete("/documents/{document_id}/tags/{tag_id}")
async def remove_tag(document_id: int, tag_id: int, db: AsyncSession = Depends(get_db)):
    document = await db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    tag = await db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    await db.refresh(document, attribute_names=["tags"])
    if tag in document.tags:
        document.tags.remove(tag)
        await db.commit()

    return {"message": "Tag removed"}


@router.delete("/documents/{document_id}")
async def delete_document(document_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    await db.delete(document)
    await db.commit()

    return {"message": "Document deleted"}
