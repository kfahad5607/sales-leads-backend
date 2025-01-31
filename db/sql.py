from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
# from sqlmodel.ext.asyncio.session import AsyncSession
from typing import AsyncIterator


DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/artisandb"
engine = create_async_engine(DB_URL, echo=True)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session