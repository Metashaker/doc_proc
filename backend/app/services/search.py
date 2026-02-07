from sqlalchemy import text


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def build_search_query(query: str):
    pattern = f"%{_escape_like(query)}%"
    sql = text(
        "SELECT id, filename, substring(coalesce(content, '') from 1 for 200) AS snippet "
        "FROM documents WHERE content ILIKE :pattern ESCAPE '\\'"
    )
    return sql, {"pattern": pattern}
