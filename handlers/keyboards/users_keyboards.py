from typing import Type

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


class UsersKeyboards:

    @staticmethod
    async def main_kb() -> ReplyKeyboardMarkup:
        kb_main = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        b_fav = KeyboardButton('Избранное')
        b_last = KeyboardButton('Последние')
        b_today = KeyboardButton('Сегодня')
        kb_main.row(b_last, b_today)
        kb_main.add(b_fav)
        return kb_main
