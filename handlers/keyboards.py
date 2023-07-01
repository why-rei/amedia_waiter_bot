from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from database.db_controller import db_anime_take, db_favorite_take_all, db_favorite_take_one, db_anime_last_take, \
    db_anime_today_take, db_ants_take, db_timetable_take_day

# Main keyboard
kb_main = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
b_fav = KeyboardButton('Избранное')
b_last = KeyboardButton('Последние')
b_today = KeyboardButton('Сегодня')
kb_main.row(b_last, b_today)
kb_main.add(b_fav)


async def kb_last_animes(check: int) -> InlineKeyboardMarkup:
    kb_last_animes_ = InlineKeyboardMarkup(row_width=2)
    anime_list = await db_anime_last_take()

    if check == 1:
        for item in anime_list[:4]:
            b_anime = InlineKeyboardButton(f'{" ".join(str(item.anime.name).split(" ")[:4])} | {item.seria} серия',
                                           callback_data=f'send_anime_{item.anime.id}')
            kb_last_animes_.add(b_anime)
        kb_last_animes_.add(InlineKeyboardButton('->', callback_data=f'last_1>'))
        kb_last_animes_.add(InlineKeyboardButton('Обновить', callback_data=f'last_update'))
    elif check == 2:
        for item in anime_list[4:8]:
            b_anime = InlineKeyboardButton(f'{" ".join(str(item.anime.name).split(" ")[:4])} | {item.seria} серия',
                                           callback_data=f'send_anime_{item.anime.id}')
            kb_last_animes_.add(b_anime)
        kb_last_animes_.row(InlineKeyboardButton('<-', callback_data=f'last_0>'),
                            InlineKeyboardButton('->', callback_data=f'last_2>'))
        kb_last_animes_.add(InlineKeyboardButton('Обновить', callback_data=f'last_update'))
    elif check == 3:
        for item in anime_list[8:12]:
            b_anime = InlineKeyboardButton(f'{" ".join(str(item.anime.name).split(" ")[:4])} | {item.seria} серия',
                                           callback_data=f'send_anime_{item.anime.id}')
            kb_last_animes_.add(b_anime)
        kb_last_animes_.add(InlineKeyboardButton('<-', callback_data=f'last_1>'))
        kb_last_animes_.add(InlineKeyboardButton('Обновить', callback_data=f'last_update'))

    return kb_last_animes_


async def kb_today_animes() -> InlineKeyboardMarkup:
    kb_today_animes_ = InlineKeyboardMarkup(row_width=2)
    anime_list = await db_anime_today_take()
    for item in anime_list:
        anime = await db_anime_take(item[1])
        b_anime = InlineKeyboardButton(
            f'{" ".join(str(anime.name).split(" ")[:3])} | {item[2]} серия в {item[3].split(" ")[-1]}',
            callback_data=f'send_anime_{anime.id}')
        kb_today_animes_.add(b_anime)
    kb_today_animes_.add(InlineKeyboardButton('Обновить', callback_data=f'today_update'))

    return kb_today_animes_


async def kb_anime(user_id: int, anime_id: int) -> InlineKeyboardMarkup:
    kb_anime_ = InlineKeyboardMarkup(row_width=1)
    anime = await db_anime_take(anime_id)
    if await db_favorite_take_one(user_id=user_id, anime_id=anime_id) is None:
        b_fav_add = InlineKeyboardButton('Добавить в избранное', callback_data=f'fav_add_{anime_id}')
    else:
        b_fav_add = InlineKeyboardButton('Удалить из избранного', callback_data=f'fav_delete_{anime_id}')
    b_view = InlineKeyboardButton('Смотреть', url=anime.link)
    kb_anime_.add(b_view)
    kb_anime_.add(b_fav_add)
    return kb_anime_


async def kb_favorite(user_id) -> InlineKeyboardMarkup:
    kb_favorite_ = InlineKeyboardMarkup(row_width=1)
    fav_obj = await db_favorite_take_all(user_id)
    for obj in fav_obj:
        anime_id = obj.anime_id
        anime_name = obj.anime.name
        b_anime = InlineKeyboardButton(anime_name, callback_data=f'send_anime_{anime_id}')
        kb_favorite_.add(b_anime)
    return kb_favorite_


async def kb_url(url):
    kb_url_ = InlineKeyboardMarkup(row_width=1)
    kb_url_.add(InlineKeyboardButton('Смотреть', url=url))
    return kb_url_


async def kb_ants() -> InlineKeyboardMarkup:
    kb_ants_ = InlineKeyboardMarkup(row_width=1)
    ants_list = await db_ants_take()
    for ant in ants_list:
        anime_id = ant[0]
        anime_name = ant[1]
        b_ant = InlineKeyboardButton(anime_name, callback_data=f'send_anime_{anime_id}')
        kb_ants_.add(b_ant)
    return kb_ants_


async def kb_timetable() -> InlineKeyboardMarkup:
    kb_timetable_ = InlineKeyboardMarkup(row_width=7)
    b_all = InlineKeyboardButton('Все расписание', callback_data='timetable_all')
    b_0 = InlineKeyboardButton('ПН', callback_data='timetable_0')
    b_1 = InlineKeyboardButton('ВТ', callback_data='timetable_1')
    b_2 = InlineKeyboardButton('СР', callback_data='timetable_2')
    b_3 = InlineKeyboardButton('ЧТ', callback_data='timetable_3')
    b_4 = InlineKeyboardButton('ПТ', callback_data='timetable_4')
    b_5 = InlineKeyboardButton('СБ', callback_data='timetable_5')
    b_6 = InlineKeyboardButton('ВС', callback_data='timetable_6')
    kb_timetable_.add(b_all)
    kb_timetable_.row(b_0, b_1, b_2, b_3, b_4, b_5, b_6)
    return kb_timetable_


async def kb_timetable_day(day: str) -> InlineKeyboardMarkup:
    kb_timetable_day_ = InlineKeyboardMarkup(row_width=2)
    timetable_obj = await db_timetable_take_day(day)
    for t_item in timetable_obj:
        anime_time = t_item.time
        anime = t_item.anime
        b_timetable_day = InlineKeyboardButton(f'{" ".join(str(anime.name).split(" ")[:3])} | {anime_time}',
                                               callback_data=f'send_anime_{anime.id}')
        kb_timetable_day_.add(b_timetable_day)

    if day == '0':
        kb_timetable_day_.add(InlineKeyboardButton('->', callback_data=f'timetable_{int(day) + 1}'))
    elif day == '6':
        kb_timetable_day_.add(InlineKeyboardButton('<-', callback_data=f'timetable_{int(day) - 1}'))
    else:
        kb_timetable_day_.row(InlineKeyboardButton('<-', callback_data=f'timetable_{int(day) - 1}'),
                              InlineKeyboardButton('->', callback_data=f'timetable_{int(day) + 1}'))

    kb_timetable_day_.add(InlineKeyboardButton('--Назад--', callback_data='timetable_back'))
    return kb_timetable_day_


# Find kb
async def kb_founded(animes_ids_list) -> InlineKeyboardMarkup:
    kb_founded_ = InlineKeyboardMarkup(row_width=1)
    for anime_id in animes_ids_list:
        anime = await db_anime_take(anime_id[0])
        b_anime = InlineKeyboardButton(anime.name, callback_data=f'send_anime_{anime.id}')
        kb_founded_.add(b_anime)
    return kb_founded_
