from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, UniqueConstraint, Table
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


document_tags = Table(
    "document_tags",
    Base.metadata,
    Column("document_id", ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    Index("ix_document_tags_document_id", "document_id"),
    Index("ix_document_tags_tag_id", "tag_id"),
)


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        Index("ix_documents_created_at", "created_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    content = Column(Text)
    file_size = Column(Integer)
    page_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    processing_status = relationship(
        "ProcessingStatus",
        back_populates="document",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    tags = relationship(
        "Tag",
        secondary=document_tags,
        back_populates="documents",
    )


class ProcessingStatus(Base):
    __tablename__ = "processing_statuses"
    __table_args__ = (
        UniqueConstraint("document_id", name="uq_processing_statuses_document_id"),
        Index("ix_processing_statuses_document_id", "document_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="completed")
    error_message = Column(Text, nullable=True)
    processed_at = Column(DateTime, nullable=True)

    document = relationship("Document", back_populates="processing_status")


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = (
        UniqueConstraint("name", name="uq_tags_name"),
        Index("ix_tags_name", "name"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship(
        "Document",
        secondary=document_tags,
        back_populates="tags",
    )
