from loguru import logger
from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageNotModified, BotBlocked, ChatNotFound

from core.settings import bot


# Start command
async def start_command(message: Message) -> None:
    await message.answer('start msg')


async def register_handlers_client(dp: Dispatcher) -> None:
    dp.register_message_handler(start_command, commands=['start'])
