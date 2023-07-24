import os

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Webhook settings
WEBHOOK_HOST = os.getenv('SERVER_URI')
WEBHOOK_PATH = '/bot'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Webserver settings
WEBAPP_HOST = '127.0.0.1'
WEBAPP_PORT = 7771

# Initialize bot, dispatcher and memory
storage = MemoryStorage()
bot = Bot(token=os.getenv('TELEGRAM_API_TOKEN'))
dp = Dispatcher(bot, storage=storage)
