import os
from typing import Type

from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from database.tables import *
from data.config import FAVORITE_LIMIT

engine = create_async_engine(
    os.getenv('POSTGRES_CONN'), pool_size=30, max_overflow=-1
)

Async_Session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


# All tables create
async def db_tables_create() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


# Users
async def db_user_add(user_id: int) -> None:
    async with Async_Session() as session, session.begin():
        if await session.get(Users, user_id) is None:
            user = Users(id=user_id)
            session.add(user)


async def db_user_take(user_id: int) -> Type[Users]:
    async with Async_Session() as session, session.begin():
        user = await session.get(Users, user_id)
        return user


# Animes
async def db_anime_add(anime_id: int, name: str, desc: str, info: str, link: str, photo_url: str) -> None:
    async with Async_Session() as session, session.begin():
        if await session.get(Animes, anime_id) is None:
            anime = Animes(id=anime_id, name=name, desc=desc, info=info, photo_url=photo_url, link=link)
            session.add(anime)


async def db_anime_take(anime_id: int) -> Type[Animes]:
    async with Async_Session() as session, session.begin():
        anime = await session.get(Animes, anime_id)
        return anime


async def db_anime_check(anime_id: int) -> bool:
    async with Async_Session() as session, session.begin():
        if await session.get(Animes, anime_id) is None:
            return True
        return False


# Last animes
async def db_anime_last_add(anime_list: list) -> None:
    async with Async_Session() as session, session.begin():
        sql = text("TRUNCATE TABLE lastanimes")
        await session.execute(sql)

        to_add_list = []
        for anime_item in anime_list:
            table_id = anime_list.index(anime_item)
            anime_id = anime_item[0]
            anime_seria = anime_item[1]
            anime_time = anime_item[2]

            last_anime = LastAnimes(id=table_id, anime_id=anime_id, seria=anime_seria, time=anime_time)
            to_add_list.append(last_anime)
        session.add_all(to_add_list)


async def db_anime_last_take() -> list[Type[LastAnimes]]:
    async with Async_Session() as session, session.begin():
        stmt = select(LastAnimes)
        db_obj = await session.scalars(stmt)
        last_anime_list = []
        for obj in db_obj:
            last_anime_list.append(obj)
        return last_anime_list


# Today animes
async def db_anime_today_add(anime_list: list) -> None:
    async with Async_Session() as session, session.begin():
        sql = text("TRUNCATE TABLE todayanimes")
        await session.execute(sql)

        to_add_list = []
        for anime_item in anime_list:
            table_id = anime_list.index(anime_item)
            anime_id = anime_item[0]
            anime_seria = anime_item[1]
            anime_time = anime_item[2]

            today_anime = TodayAnimes(id=table_id, anime_id=anime_id, seria=anime_seria, time=anime_time)
            to_add_list.append(today_anime)
        session.add_all(to_add_list)


async def db_anime_today_take() -> list:
    async with Async_Session() as session, session.begin():
        stmt = select(TodayAnimes).order_by(TodayAnimes.id)
        db_obj = await session.scalars(stmt)
        today_anime_list = []
        for obj in db_obj:
            today_anime_list.append((obj.id, obj.anime_id, obj.seria, obj.time))
        return today_anime_list


# Ants
async def db_ants_take() -> list:
    async with Async_Session() as session, session.begin():
        stmt = select(Ants)
        db_obj = await session.scalars(stmt)
        ants_list = []
        for i in db_obj:
            ants_list.append((i.anime_id, i.name))
        return ants_list


async def db_ants_update(anime_list) -> None:
    async with Async_Session() as session, session.begin():
        sql = text("TRUNCATE TABLE ants")
        await session.execute(sql)

        for anime in anime_list:
            ants_item = Ants(anime_id=anime[0], name=anime[1])
            session.add(ants_item)


# Timetable
async def db_timetable_take_day(day: str) -> Type[Timetable]:
    async with Async_Session() as session, session.begin():
        stmt = select(Timetable).where(Timetable.day.in_([day]))
        timetable_obj = await session.scalars(stmt)
        return timetable_obj


async def db_timetable_take_all() -> str:
    async with Async_Session() as session, session.begin():
        stmt = select(Timetable).order_by(Timetable.id)
        db_obj = await session.scalars(stmt)
        day_dict = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг',
                    4: 'Пятница', 5: 'Суббота', 6: 'Воскресение'}
        timetable_str = ''
        day_num = 0
        for i in db_obj:
            if str(day_num) == i.day:
                timetable_str += f'\n{day_dict[day_num]}: \n'
                day_num += 1
            anime_time = i.time
            anime = i.anime
            timetable_str += f'{anime.name} | {anime_time}\n'
        return timetable_str


async def db_timetable_update(timetable_list: list) -> None:
    async with Async_Session() as session, session.begin():
        sql_truncate = text("TRUNCATE TABLE timetable")
        await session.execute(sql_truncate)

        for t_item in timetable_list:
            anime_id = t_item[0]
            anime_day = t_item[1]
            anime_time = t_item[2]

            t_item_ = Timetable(anime_id=anime_id, day=anime_day, time=anime_time)
            session.add(t_item_)


# Favorite
async def db_favorite_add(user_id: int, anime_id: int) -> str:
    await db_user_add(user_id)

    async with Async_Session() as session, session.begin():
        user = await session.get(Users, user_id)
        user_fav_count = user.fav_count

        if user_fav_count < FAVORITE_LIMIT:
            stmt = select(Favorite).where(Favorite.user_id.in_([user_id])).where(Favorite.anime_id.in_([anime_id]))
            db_obj = await session.scalar(stmt)

            if db_obj is None:
                fav_item = Favorite(user_id=user_id, anime_id=anime_id)
                user.fav_count += 1
                session.add_all([fav_item, user])

                return 'good'
            else:
                return 'error_already_have'
        else:
            return 'error_limit'


async def db_favorite_delete(user_id: int, anime_id: int) -> str:
    async with Async_Session() as session, session.begin():
        user = await session.get(Users, user_id)
        stmt = select(Favorite).where(Favorite.user_id.in_([user_id])).where(Favorite.anime_id.in_([anime_id]))
        db_obj = await session.scalar(stmt)
        if db_obj is not None:
            await session.delete(db_obj)
            await session.flush()
            user.fav_count -= 1
            return 'good'
        return 'bad'


async def db_favorite_take_all(user_id: int) -> Type[Favorite]:
    async with Async_Session() as session, session.begin():
        stmt = select(Favorite).where(Favorite.user_id.in_([user_id]))
        fav_obj = await session.scalars(stmt)
        return fav_obj


async def db_favorite_take_one(user_id: int, anime_id: int) -> Type[Favorite]:
    async with Async_Session() as session, session.begin():
        sql = text(f"SELECT anime_id FROM favorite WHERE user_id = {user_id} and anime_id = {anime_id}")
        resp = await session.execute(sql)
        return resp.fetchone()


# Notice
@logger.catch()
async def db_notice_add() -> None:
    last_animes_list = await db_anime_last_take()
    for item in last_animes_list:
        async with Async_Session() as session, session.begin():
            anime_id = item.anime.id
            anime_seria = item.seria

            sql = text(f"SELECT * FROM notice WHERE anime_id = {anime_id} and seria = '{anime_seria}'")
            resp = await session.execute(sql)
            resp_anime = resp.fetchone()

            if resp_anime is None:
                # Notice add
                anime_notice = Notice(anime_id=anime_id, seria=anime_seria)
                session.add(anime_notice)
                logger.info(f'Add to notice: name: "{anime_id}" seria: "{anime_seria}"')


@logger.catch()
async def db_notice_take() -> list:
    notice_list = []
    async with Async_Session() as session, session.begin():
        stmt = select(Notice).where(Notice.checker.in_([False]))
        anime_notice_list = await session.scalars(stmt)
        for notice_obj in anime_notice_list.fetchall():
            anime_id = notice_obj.anime_id
            anime_seria = notice_obj.seria
            sql_fav = text(f"SELECT user_id FROM favorite WHERE anime_id = {anime_id}")
            resp_fav = await session.execute(sql_fav)
            users_ids_list = resp_fav.fetchall()
            anime_item = await session.get(Animes, anime_id)
            notice_list.append((anime_item, anime_seria, users_ids_list))
    return notice_list


async def db_notice_update_checker(anime_id: int, anime_seria: str) -> None:
    async with Async_Session() as session, session.begin():
        sql = text(f"UPDATE notice SET checker=true WHERE anime_id = {anime_id} and seria = '{anime_seria}'")
        await session.execute(sql)


# Find anime
async def db_find_anime(anime_name: str) -> list[Animes]:
    async with Async_Session() as session, session.begin():
        sql = text(f"SELECT id FROM animes WHERE name LIKE '{anime_name}%'")
        resp = await session.execute(sql)
        animes_ids_list = resp.fetchall()
        return animes_ids_list
