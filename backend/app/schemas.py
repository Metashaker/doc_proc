from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class DocumentBase(BaseModel):
    filename: str


class DocumentCreate(DocumentBase):
    pass


class TagSummary(BaseModel):
    id: int
    name: str


class DocumentResponse(DocumentBase):
    id: int
    file_size: Optional[int] = None
    page_count: Optional[int] = None
    status: str
    created_at: datetime
    tags: List[TagSummary] = Field(default_factory=list)

    class Config:
        from_attributes = True


class DocumentDetail(DocumentResponse):
    content: Optional[str] = None


class TagResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class TagCreate(BaseModel):
    name: str


class SearchResult(BaseModel):
    id: int
    filename: str
    snippet: str
