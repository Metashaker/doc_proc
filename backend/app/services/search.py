from sqlalchemy import text


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def build_search_query(query: str):
    pattern = f"%{_escape_like(query)}%"
    sql = text(
        "SELECT DISTINCT documents.id, documents.filename, "
        "substring(coalesce(documents.content, '') from 1 for 200) AS snippet "
        "FROM documents "
        "LEFT JOIN document_tags ON documents.id = document_tags.document_id "
        "LEFT JOIN tags ON tags.id = document_tags.tag_id "
        "WHERE documents.content ILIKE :pattern ESCAPE '\\' "
        "OR documents.filename ILIKE :pattern ESCAPE '\\' "
        "OR tags.name ILIKE :pattern ESCAPE '\\'"
    )
    return sql, {"pattern": pattern}
