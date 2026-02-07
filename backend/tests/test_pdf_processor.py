import os
import sys

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.pdf_processor import extract_text_from_pdf


@pytest.mark.asyncio
async def test_extract_text_from_pdf_invalid(tmp_path):
    file_path = tmp_path / "not_a_pdf.pdf"
    file_path.write_bytes(b"not a real pdf")

    with pytest.raises(ValueError):
        await extract_text_from_pdf(str(file_path))
