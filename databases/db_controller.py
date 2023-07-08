import os
from typing import Type

from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from databases.postgres_tables import Base

engine = create_async_engine(
    os.getenv('POSTGRES_CONN'), pool_size=30, max_overflow=-1
)

Async_Session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


# All tables create
async def db_tables_create() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

# async with Async_Session() as session, session.begin():
