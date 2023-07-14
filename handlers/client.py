from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from loguru import logger

from core.settings import bot
from handlers.keyboards import UsersKeyboards


# Start command
async def start_command(message: Message) -> None:
    await message.answer('start msg', reply_markup=await UsersKeyboards.main_kb())


async def register_handlers_client(dp: Dispatcher) -> None:
    dp.register_message_handler(start_command, commands=['start'])
