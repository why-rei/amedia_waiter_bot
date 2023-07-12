from typing import List, Tuple

from sqlalchemy import select, text
from loguru import logger

from databases.postgres_engine import engine, Async_Session
from databases.postgres_tables import Base, Animes, LastAnimes, TodayAnimes


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
    async def add_anime(pk: int, name: str, desc: str, info: str, photo_url: str, url: str) -> None:
        async with Async_Session() as session, session.begin():
            anime = Animes(id=pk, name=name, desc=desc, info=info, photo_url=photo_url, link=url)
            session.add(anime)

    @staticmethod
    def _truncate_table(session, table_name):
        return session.execute(text(f'TRUNCATE TABLE {table_name} RESTART IDENTITY;'))

    async def update_last_animes(self, animes: List[Tuple[int, str, str]]) -> None:
        async with Async_Session() as session, session.begin():
            table_name = LastAnimes.__name__.lower()
            last_animes = []
            for pk, seria, time in animes:
                last_anime = LastAnimes(anime_id=pk, seria=seria, time=time)
                last_animes.append(last_anime)
            await self._truncate_table(session=session, table_name=table_name)
            session.add_all(last_animes)

    async def update_today_animes(self, animes: List[Tuple[int, str, str]]) -> None:
        async with Async_Session() as session, session.begin():
            table_name = TodayAnimes.__name__.lower()
            today_animes = []
            for pk, seria, time in animes:
                today_anime = TodayAnimes(anime_id=pk, seria=seria, time=time)
                today_animes.append(today_anime)
            await self._truncate_table(session=session, table_name=table_name)
            session.add_all(today_animes)


if __name__ == '__main__':
    import asyncio

    asyncio.run(postgres_tables_create())
