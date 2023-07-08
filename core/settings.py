import os

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv


load_dotenv()

# Initialize bot, dispatcher and memory
storage = MemoryStorage()
bot = Bot(token=os.getenv('TELEGRAM_API_TOKEN'))
dp = Dispatcher(bot, storage=storage)
