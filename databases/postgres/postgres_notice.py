from collections import namedtuple
from typing import List, Type

from sqlalchemy import select, update

from ._postgres_engine import Async_Session
from ._postgres_tables import LastAnimes, Notice, Favorite, Animes


class PostgresNotice:
    @staticmethod
    async def get_all_last_animes() -> List[Type[LastAnimes]]:
        async with Async_Session() as session, session.begin():
            stmt = select(LastAnimes).order_by(LastAnimes.id.desc())
            resp = await session.execute(stmt)
            return resp.all()

    @staticmethod
    async def check_notice(anime_id: int, anime_seria: str) -> int:
        async with Async_Session() as session, session.begin():
            stmt = select(Notice).where(Notice.anime_id == anime_id, Notice.seria == anime_seria)
            resp = await session.execute(stmt)
            return 1 if resp.all() else 0

    @staticmethod
    async def update_notice(notice_animes: List[Type[namedtuple]]) -> None:
        async with Async_Session() as session, session.begin():
            notice_to_add = []
            for anime in notice_animes:
                notice_to_add.append(Notice(anime_id=anime.id, seria=anime.seria))
            session.add_all(notice_to_add)

    @staticmethod
    async def get_notices() -> List[Type[Notice]]:
        async with Async_Session() as session, session.begin():
            stmt = select(Notice).where(Notice.checker == 0).order_by(Notice.id)
            resp = await session.execute(stmt)
            return resp.all()

    @staticmethod
    async def get_users_favorites(anime_id: int) -> List[Type[Favorite]]:
        async with Async_Session() as session, session.begin():
            stmt = select(Favorite.user_id).where(Favorite.anime_id == anime_id)
            resp = await session.execute(stmt)
            return resp.all()

    @staticmethod
    async def get_anime(anime_id: int) -> Type[Animes]:
        async with Async_Session() as session, session.begin():
            return await session.get(Animes, anime_id)

    @staticmethod
    async def turn_notice_checker(notice_id: int) -> None:
        async with Async_Session() as session, session.begin():
            stmt = update(Notice).where(Notice.id == notice_id).values(checker=1)
            await session.execute(stmt)
