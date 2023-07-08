from typing import Type

from loguru import logger
from sqlalchemy import select, text

from postgres_engine import engine, Async_Session
from databases.postgres_tables import Base


# All postgres tables create
async def postgres_tables_create() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

# async with Async_Session() as session, session.begin():
