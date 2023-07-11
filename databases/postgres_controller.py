from typing import List, Sequence

from sqlalchemy import select, text
from loguru import logger

from .postgres_engine import engine, Async_Session
from databases.postgres_tables import Base, Animes


# All postgres tables create
async def postgres_tables_create() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


class PostgresController:

    @staticmethod
    async def check_animes_ids(animes_ids: List[int]) -> List[int]:
        async with Async_Session() as session, session.begin():
            stmt = select(Animes.id).where(Animes.id.in_(animes_ids))
            db_response = await session.scalars(stmt)
            identified_animes = db_response.all()

            return [animes_ids.index(x) for x in animes_ids if x not in identified_animes]

    @staticmethod
    async def add_anime(pk, name, desc, info, photo_url, url) -> None:
        async with Async_Session() as session, session.begin():
            anime = Animes(id=pk, name=name, desc=desc, info=info, photo_url=photo_url, link=url)
            session.add(anime)


if __name__ == '__main__':
    import asyncio

    lll = [1438, 936, 7777, 1436, 9999]
    r = asyncio.run(PostgresController().check_animes_ids(lll))
    print(r)
