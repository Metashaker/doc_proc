import fitz


async def extract_text_from_pdf(file_path: str) -> tuple[str, int]:
    try:
        doc = fitz.open(file_path)
    except Exception as exc:
        raise ValueError("Invalid or corrupted PDF") from exc

    text_parts = []
    for page in doc:
        text_parts.append(page.get_text())
    page_count = len(doc)
    doc.close()
    return "".join(text_parts), page_count
