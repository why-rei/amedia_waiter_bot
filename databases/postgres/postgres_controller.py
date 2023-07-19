from datetime import datetime
from typing import Type, List, Tuple

from sqlalchemy import select, text, delete

from data.config import USER_FAV_LIMIT
from databases.postgres._postgres_engine import engine, Async_Session
from databases.postgres._postgres_tables import Base, Animes, LastAnimes, TodayAnimes, Ants, Timetable, Users, Favorite


class PostgresController:

    @staticmethod
    async def postgres_tables_create() -> None:
        """Create all postgres tables"""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()

    # Users
    @staticmethod
    def _get_user(session: Type[Async_Session], user_id: int) -> Type[Async_Session]:
        return session.get(Users, user_id)

    async def _update_user(self, session: Type[Async_Session], user_id: int, fav: int = 0):
        user = await self._get_user(session=session, user_id=user_id)
        if user:
            user.fav_count += fav
            user.last_update = datetime.now()
            return session.add(user)
        else:
            new_user = Users(id=user_id)
            return session.add(new_user)

    async def mark_user(self, user_id: int) -> None:
        async with Async_Session() as session, session.begin():
            await self._update_user(session=session, user_id=user_id)

    @staticmethod
    def _get_user_fav(session: Type[Async_Session], user_id: int, anime_id: int = None) -> Type[Async_Session]:
        if anime_id:
            stmt = select(Favorite).where(Favorite.anime_id == anime_id, Favorite.user_id == user_id)
        else:
            stmt = select(Favorite).where(Favorite.user_id == user_id).join(Animes).order_by(Animes.name)
        return session.execute(stmt)

    async def get_user_faves(self, user_id: int):
        async with Async_Session() as session, session.begin():
            user_faves = await self._get_user_fav(session=session, user_id=user_id)
            return user_faves.all()

    async def add_user_fav(self, user_id, anime_id) -> Tuple[int, Type[Animes]]:
        async with Async_Session() as session, session.begin():
            anime = await self._get_anime(session=session, anime_id=anime_id)

            user_fav = await self._get_user_fav(session=session, user_id=user_id, anime_id=anime_id)
            user = await self._get_user(session=session, user_id=user_id)
            if user.fav_count >= USER_FAV_LIMIT:
                return 2, anime
            elif not user_fav.all():
                fav = Favorite(user_id=user_id, anime_id=anime_id)
                session.add(fav)
                await self._update_user(session=session, user_id=user_id, fav=1)
                return 1, anime
            return 0, anime

    async def del_user_fav(self, user_id: int, anime_id: int) -> Tuple[int, Type[Animes]]:
        async with Async_Session() as session, session.begin():
            anime = await self._get_anime(session=session, anime_id=anime_id)

            user_fav = await self._get_user_fav(session=session, user_id=user_id, anime_id=anime_id)
            if user_fav.all():
                stmt = delete(Favorite).where(Favorite.user_id == user_id, Favorite.anime_id == anime_id)
                await session.execute(stmt)
                await self._update_user(session=session, user_id=user_id, fav=-1)
                return 1, anime
            return 0, anime

    # Add and update animes
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
            for anime_id in animes_ids:
                ant_anime = Ants(anime_id=anime_id)
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

    # Get animes for user
    @staticmethod
    def _get_anime(session: Type[Async_Session], anime_id: int) -> Type[Animes]:
        return session.get(Animes, anime_id)

    async def get_anime(self, user_id: int, anime_id: int) -> Type[Animes]:
        async with Async_Session() as session, session.begin():
            await self._update_user(session=session, user_id=user_id)
            return await self._get_anime(session=session, anime_id=anime_id)

    async def get_anime_view(self, anime_id: int, user_id: int) -> Tuple[Type[Animes], int]:
        async with Async_Session() as session, session.begin():
            await self._update_user(session=session, user_id=user_id)

            anime = await self._get_anime(session=session, anime_id=anime_id)
            resp = await self._get_user_fav(session=session, user_id=user_id, anime_id=anime_id)
            user_fav_check = 1 if resp.all() else 0
            return anime, user_fav_check

    async def get_last_animes(self, user_id: int, start: int, end: int) -> List[Type[LastAnimes]]:
        async with Async_Session() as session, session.begin():
            await self._update_user(session=session, user_id=user_id)

            stmt = select(LastAnimes).filter(LastAnimes.id.in_(range(start, end))).order_by(LastAnimes.id)
            db_response = await session.scalars(stmt)
            last_animes = db_response.all()
            return last_animes

    async def get_today_animes(self, user_id: int) -> List[Type[TodayAnimes]]:
        async with Async_Session() as session, session.begin():
            await self._update_user(session=session, user_id=user_id)

            stmt = select(TodayAnimes).order_by(TodayAnimes.id)
            db_response = await session.scalars(stmt)
            today_animes = db_response.all()
            return today_animes

    async def get_ants_animes(self, user_id: int) -> List[Type[Ants]]:
        async with Async_Session() as session, session.begin():
            await self._update_user(session=session, user_id=user_id)

            stmt = select(Ants).order_by(Ants.id)
            db_response = await session.scalars(stmt)
            ants_animes = db_response.all()
            return ants_animes

    async def get_timetable_animes(self, user_id: int, day: str) -> List[Type[Timetable]]:
        async with Async_Session() as session, session.begin():
            await self._update_user(session=session, user_id=user_id)

            if day.isdigit():
                day = int(day)
                stmt = select(Timetable).where(Timetable.day == day).order_by(Timetable.day)
            elif day == 'all':
                stmt = select(Timetable).order_by(Timetable.day)
            db_response = await session.scalars(stmt)
            timetable_animes = db_response.all()
            return timetable_animes

    async def find_animes(self, user_id: int, user_req: str) -> List[Type[Animes]]:
        async with Async_Session() as session, session.begin():
            await self._update_user(session=session, user_id=user_id)

            stmt = select(Animes).filter(Animes.name.ilike(f'%{user_req}%')).order_by(Animes.name)
            animes = await session.execute(stmt)
            return animes.all()


if __name__ == '__main__':
    import asyncio

    # r = asyncio.run(PostgresController().find_anime(user_id=, user_req='Месть'))
    # print(r)
    # for i in r:
    #     print(i)
