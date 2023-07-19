import tzlocal
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import executor
from loguru import logger

from settings import dp
from databases import PostgresController
from handlers.client import register_handlers_client
from parcer_conn import ParcerConn


async def scheduler():
    scheduler_a = AsyncIOScheduler(timezone=str(tzlocal.get_localzone()))

    scheduler_a.add_job(ParcerConn().update_main, trigger='interval', seconds=180)
    scheduler_a.add_job(ParcerConn().update_secondary, trigger='cron', hour=00)

    scheduler_a.start()


async def on_startup(_):
    await PostgresController.postgres_tables_create()
    await register_handlers_client(dp)

    await ParcerConn().update_main()
    await ParcerConn().update_secondary()

    await scheduler()

    print('Bot is Online')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
