from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from sqlalchemy.orm import declarative_base

from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_db():
    async with async_session() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
        await conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_documents_content_trgm "
                "ON documents USING GIN (content gin_trgm_ops);"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE processing_statuses "
                "DROP CONSTRAINT IF EXISTS processing_statuses_document_id_fkey;"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE processing_statuses "
                "ADD CONSTRAINT processing_statuses_document_id_fkey "
                "FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE;"
            )
        )
