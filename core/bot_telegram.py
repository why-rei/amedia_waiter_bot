import tzlocal
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import executor
from loguru import logger

from settings import dp
from databases import postgres_tables_create
from handlers.client import register_handlers_client
from parcer import ParcerConn
from notice_sys import NoticeSys


async def main():
    try:
        await ParcerConn().update_main()
        await NoticeSys().notice()
    except Exception as e:
        logger.exception(e)


async def secondary():
    try:
        await ParcerConn().update_ants()
        await ParcerConn().update_timetable()
    except Exception as e:
        logger.exception(e)


async def scheduler():
    scheduler_a = AsyncIOScheduler(timezone=str(tzlocal.get_localzone()))

    scheduler_a.add_job(main, trigger='interval', seconds=180)
    scheduler_a.add_job(secondary, trigger='cron', hour=00)

    scheduler_a.start()


async def on_startup(_):
    try:
        await postgres_tables_create()
        await register_handlers_client(dp)

        await main()
        await secondary()

        await scheduler()

    except Exception as e:
        logger.exception(e)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
