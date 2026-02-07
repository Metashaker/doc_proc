from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import SearchResult
from app.services.search import build_search_query

router = APIRouter()


@router.get("/search")
async def search_documents(q: str, db: AsyncSession = Depends(get_db)):
    query, params = build_search_query(q)
    result = await db.execute(query, params)
    rows = result.fetchall()

    results = []
    for row in rows:
        content = row[2] or ""
        snippet = content[:200] + "..." if len(content) > 200 else content
        results.append(
            SearchResult(
                id=row[0],
                filename=row[1],
                snippet=snippet,
            )
        )

    return results
