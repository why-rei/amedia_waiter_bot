import tzlocal
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import executor

from settings import dp
from databases import postgres_tables_create
from handlers.client import register_handlers_client


async def on_startup(_):
    await postgres_tables_create()

    await register_handlers_client(dp)

    print('Bot is Online')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
