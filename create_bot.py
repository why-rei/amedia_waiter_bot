import os
import sys
from loguru import logger
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher

# Configure logging
LOGGER_FORMAT = "<b><k><M>{level}</></></>\t|" \
                "\t<g>{time:YYYY-MM-DD > HH:mm:ss}</>\t|" \
                "\t<light-yellow>{message}</>\t::\t<c>{function}</>"
logger.remove(0)
logger.add(sys.stderr, level="INFO", format=LOGGER_FORMAT)
logger.add("logs/main.log", level="INFO", format=LOGGER_FORMAT, rotation="1 week", compression="zip")

# Initialize bot and dispatcher and memory
storage = MemoryStorage()
bot = Bot(token=os.getenv('TELEGRAM_API_TOKEN'))
dp = Dispatcher(bot, storage=storage)
