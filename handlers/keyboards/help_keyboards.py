from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def help_keyboard():
    help_keyboard_ = InlineKeyboardMarkup(row_width=1)

    b_how_add_anime = InlineKeyboardButton('Как добавить аниме?', callback_data='help_add')
    b_reply_kb = InlineKeyboardButton('Пропали кнопки?', callback_data='help_replykb')
    b_donate = InlineKeyboardButton('Задонатить?', callback_data='help_donate')

    help_keyboard_.add(b_how_add_anime, b_reply_kb, b_donate)

    return help_keyboard_
