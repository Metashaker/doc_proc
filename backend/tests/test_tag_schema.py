from datetime import datetime
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.schemas import DocumentResponse, TagSummary


def test_document_response_defaults_tags():
    doc = DocumentResponse(
        id=1,
        filename="sample.pdf",
        status="completed",
        created_at=datetime.utcnow(),
    )
    assert doc.tags == []


def test_document_response_accepts_tags():
    doc = DocumentResponse(
        id=1,
        filename="sample.pdf",
        status="completed",
        created_at=datetime.utcnow(),
        tags=[TagSummary(id=1, name="legal")],
    )
    assert doc.tags[0].name == "legal"
