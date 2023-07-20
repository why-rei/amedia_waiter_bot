from collections import namedtuple
from typing import List, Type, Tuple

from sqlalchemy import select

from databases.postgres._postgres_engine import Async_Session
from databases.postgres._postgres_tables import LastAnimes, Notice


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
            stmt = select(Notice).where(Notice.anime_id.in_([anime_id]).__and__(Notice.seria.in_([anime_seria])))
            resp = await session.execute(stmt)
            return 1 if resp.all() else 0

    @staticmethod
    async def update_notice(notice_animes: List[Type[namedtuple]]) -> None:
        async with Async_Session() as session, session.begin():
            notice_to_add = []
            for anime in notice_animes:
                notice_to_add.append(Notice(anime_id=anime.id, seria=anime.seria))
            session.add_all(notice_to_add)
