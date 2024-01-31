import asyncio

from sqlalchemy import select

from databases.postgres._postgres_engine import Async_Session
from databases.postgres._postgres_tables import Animes


async def fix_db_urls():
    async with Async_Session() as session, session.begin():
        items_list = await session.execute(select(Animes))

        for db_item in items_list.scalars():
            db_item: Animes
            db_item.link = db_item.link.split('/')[-1]
            db_item.photo_url = '/uploads' + db_item.photo_url.split('/uploads')[-1]

if __name__ == '__main__':

    asyncio.run(fix_db_urls())
