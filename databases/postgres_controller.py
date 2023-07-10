from sqlalchemy import select, text
from loguru import logger

from postgres_engine import engine, Async_Session
from databases.postgres_tables import Base


# All postgres tables create
async def postgres_tables_create() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


# async with Async_Session() as session, session.begin():
class PostgresAnimes:

    @staticmethod
    async def check_anime(anime_id: int) -> bool:
        pass

    async def initializing_anime(self):
        pass


if __name__ == '__main__':
    r = ''
    print(r)
