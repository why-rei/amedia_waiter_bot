import tzlocal
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import executor
from loguru import logger

from settings import dp, bot, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT
from databases import postgres_tables_create
from handlers.client import register_handlers_client
from parcer import ParcerConn
from notice_sys import NoticeSys


async def main() -> None:
    try:
        await ParcerConn().update_main()
        await NoticeSys().notice()
    except Exception as e:
        logger.exception(e)


async def secondary() -> None:
    try:
        await ParcerConn().update_ants()
        await ParcerConn().update_timetable()
    except Exception as e:
        logger.exception(e)


async def scheduler() -> None:
    scheduler_a = AsyncIOScheduler(timezone=str(tzlocal.get_localzone()))

    scheduler_a.add_job(main, trigger='interval', seconds=180)
    scheduler_a.add_job(secondary, trigger='cron', hour=00)

    scheduler_a.start()


async def on_startup(_) -> None:
    try:
        webhook_info = bot.get_webhook_info()
        if webhook_info.url != WEBHOOK_URL:
            await bot.set_webhook(WEBHOOK_URL)

        await postgres_tables_create()
        await register_handlers_client(dp)

        await main()
        await secondary()

        await scheduler()

    except Exception as e:
        logger.exception(e)


async def on_shutdown(_) -> None:
    await bot.session.close()


if __name__ == '__main__':
    executor.start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
