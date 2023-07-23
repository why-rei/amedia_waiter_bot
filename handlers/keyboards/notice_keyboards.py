from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class NoticesKeyboards:
    @staticmethod
    async def notice_kb(anime_url: str) -> InlineKeyboardMarkup:
        notice_kb_ = InlineKeyboardMarkup(row_width=1)
        notice_kb_.add(InlineKeyboardButton('Смотреть', url=anime_url))
        return notice_kb_
