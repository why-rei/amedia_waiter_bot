from typing import Type

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from databases import PostgresController


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

    @staticmethod
    async def anime_kb(anime_id: int, user_fav_check: int, url: str) -> InlineKeyboardMarkup:
        anime_kb_ = InlineKeyboardMarkup(row_width=1)
        anime_kb_.add(InlineKeyboardButton('Смотреть', url=url))
        if not user_fav_check:
            anime_kb_.add(InlineKeyboardButton('Добавить в избранное', callback_data=f'fav_add_{anime_id}'))
        else:
            anime_kb_.add(InlineKeyboardButton('Удалить из избранного', callback_data=f'fav_del_{anime_id}'))
        return anime_kb_

    @staticmethod
    async def fav_kb(user_id: int) -> InlineKeyboardMarkup:
        fav_kb_ = InlineKeyboardMarkup(row_width=1)
        user_faves = await PostgresController().get_user_faves(user_id=user_id)
        for fav in user_faves:
            anime = fav[0].anime
            fav_kb_.add(InlineKeyboardButton(anime.name, callback_data=f'anime_{anime.id}'))
        return fav_kb_

    @staticmethod
    async def last_kb(user_id: int, n: int = 1) -> InlineKeyboardMarkup:
        count_last_animes = 12
        count_out = 4
        end = count_out * n + 1
        start = end - count_out
        last_animes = await PostgresController().get_last_animes(user_id=user_id, start=start, end=end)

        last_kb_ = InlineKeyboardMarkup(row_width=2)
        b_right = InlineKeyboardButton('->', callback_data=f'last_{n + 1}')
        b_left = InlineKeyboardButton('<-', callback_data=f'last_{n - 1}')
        b_update = InlineKeyboardButton('Обновить', callback_data=f'last_1')

        for item in last_animes:
            b_anime = InlineKeyboardButton(f'{" ".join(str(item.anime.name).split()[:4])} | {item.seria} серия',
                                           callback_data=f'anime_{item.anime_id}')
            last_kb_.add(b_anime)

        if start == 1:
            last_kb_.add(b_right)
        elif end == count_last_animes + 1:
            last_kb_.add(b_left)
        else:
            last_kb_.row(b_left, b_right)
        last_kb_.add(b_update)

        return last_kb_

    @staticmethod
    async def today_kb(user_id: int) -> InlineKeyboardMarkup:
        last_animes = await PostgresController().get_today_animes(user_id=user_id)

        today_kb_ = InlineKeyboardMarkup(row_width=1)
        b_update = InlineKeyboardButton('Обновить', callback_data=f'today_')

        for item in last_animes:
            b_anime = InlineKeyboardButton(f'{" ".join(str(item.anime.name).split()[:3])} | '
                                           f'{item.seria} серия в {item.time.split()[-1]}',
                                           callback_data=f'anime_{item.anime_id}')
            today_kb_.add(b_anime)
        today_kb_.add(b_update)

        return today_kb_

    @staticmethod
    async def ants_kb(user_id: int) -> InlineKeyboardMarkup:
        last_animes = await PostgresController().get_ants_animes(user_id=user_id)

        today_kb_ = InlineKeyboardMarkup(row_width=1)
        b_update = InlineKeyboardButton('Обновить', callback_data=f'ants_')

        for item in last_animes:
            b_anime = InlineKeyboardButton(f'{item.anime.name}', callback_data=f'anime_{item.anime_id}')
            today_kb_.add(b_anime)
        today_kb_.add(b_update)

        return today_kb_
