from datetime import datetime
from typing import Type, List, Tuple

from sqlalchemy import select, text

from databases.postgres._postgres_engine import engine, Async_Session
from databases.postgres._postgres_tables import Base, Animes, LastAnimes, TodayAnimes, Ants, Timetable, Users


# All postgres tables create
async def postgres_tables_create() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


class PostgresAnimes:

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

    async def update_ants(self, animes_ids: List[int]) -> None:
        async with Async_Session() as session, session.begin():
            table_name = Ants.__name__.lower()
            ants_animes = []
            for pk in animes_ids:
                ant_anime = Ants(anime_id=pk)
                ants_animes.append(ant_anime)
            await self._truncate_table(session=session, table_name=table_name)
            session.add_all(ants_animes)

    async def update_timetable(self, animes: List[Tuple[int, int, str]]) -> None:
        async with Async_Session() as session, session.begin():
            table_name = Timetable.__name__.lower()
            timetable = []
            for pk, day, time in animes:
                timetable_anime = Timetable(anime_id=pk, day=day, time=time)
                timetable.append(timetable_anime)
            await self._truncate_table(session=session, table_name=table_name)
            session.add_all(timetable)


class PostgresUsers:

    @staticmethod
    def _get_user(session: Type[Async_Session], user_id: int):
        return session.get(Users, user_id)

    async def update_user(self, user_id: int, fav: int = 0):
        async with Async_Session() as session, session.begin():
            user = await self._get_user(session=session, user_id=user_id)
            if user:
                user.fav_count += fav
                user.last_update = datetime.now()
                session.add(user)

    async def add_user(self, user_id: int):
        async with Async_Session() as session, session.begin():
            user = await self._get_user(session=session, user_id=user_id)
            if not user:
                new_user = Users(id=user_id)
                session.add(new_user)
            else:
                await self.update_user(user_id=user_id)


if __name__ == '__main__':
    import asyncio

    asyncio.run(PostgresUsers().update_user(9999, 1))
