import tzlocal
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import executor
from create_bot import dp
from database.db_controller import db_tables_create
from handlers.client import register_handlers_client, notice_and_main_parce
from amedia_parcer import ants_parce, timetable_parce


def scheduler():
    scheduler_a = AsyncIOScheduler(timezone=str(tzlocal.get_localzone()))

    scheduler_a.add_job(notice_and_main_parce, trigger='interval', seconds=180)
    scheduler_a.add_job(ants_parce, trigger='interval', hours=24)
    scheduler_a.add_job(timetable_parce, trigger='interval', hours=36)

    scheduler_a.start()


async def on_startup(_):
    try:
        await db_tables_create()
        await register_handlers_client(dp)

        await notice_and_main_parce()
        await ants_parce()
        await timetable_parce()

        scheduler()
    except Exception as e:
        logger.exception(e)
        raise e


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
