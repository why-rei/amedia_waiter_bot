from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.exceptions import MessageNotModified
from loguru import logger

from data.config import DAYS, FIND_MSGS
from handlers.keyboards import UsersKeyboards
from databases import PostgresController
from data import START_MESSAGE


class AnimeFind(StatesGroup):
    anime_name = State()


"""Messages handlers"""


async def start_command(message: Message) -> None:
    user_id = message.from_user.id
    await PostgresController().mark_user(user_id=user_id)
    await message.answer(START_MESSAGE, reply_markup=await UsersKeyboards.main_kb())


async def fav_command(message: Message) -> None:
    user_id = message.from_user.id
    await message.answer('Избранное:', reply_markup=await UsersKeyboards.fav_kb(user_id=user_id))


async def lasts_command(message: Message) -> None:
    user_id = message.from_user.id
    await message.answer('Последние:', reply_markup=await UsersKeyboards.last_kb(user_id=user_id))


async def today_command(message: Message) -> None:
    user_id = message.from_user.id
    await message.answer('Сегодня:', reply_markup=await UsersKeyboards.today_kb(user_id=user_id))


async def ants_command(message: Message) -> None:
    user_id = message.from_user.id
    await message.answer('Анонсы:', reply_markup=await UsersKeyboards.ants_kb(user_id=user_id))


async def timetable_command(message: Message) -> None:
    user_id = message.from_user.id
    await message.answer('Расписание:', reply_markup=await UsersKeyboards.timetable_kb(user_id=user_id))


async def find_command(message: Message) -> None:
    user_id = message.from_user.id
    await message.answer('[--Поиск--]', reply_markup=await UsersKeyboards.find_start_kb(user_id=user_id))


async def finding_anime(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    await state.update_data(anime_name=message.text)
    user_data = await state.get_data()
    user_req = user_data["anime_name"]
    await message.answer(FIND_MSGS['found'],
                         reply_markup=await UsersKeyboards.find_animes_kb(user_id=user_id, user_req=user_req))
    await state.finish()


"""Callbacks handlers"""


async def anime_callback(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    anime_id = int(callback.data.split('_')[1])
    anime, user_fav_check = await PostgresController().get_anime_view(anime_id=anime_id, user_id=user_id)
    await callback.message.answer_photo(anime.photo_url, f'{anime.name}\n\n{anime.info}\n\n{anime.desc}',
                                        reply_markup=await UsersKeyboards.anime_kb(anime_id=anime_id,
                                                                                   user_fav_check=user_fav_check,
                                                                                   url=anime.link))
    await callback.answer(cache_time=2)


async def fav_callback(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    cd = callback.data.split('_')
    req = cd[1]
    anime_id = int(cd[2])
    if req == 'add':
        resp, anime = await PostgresController().add_user_fav(user_id=user_id, anime_id=anime_id)
        if resp == 1:
            await callback.answer(f'Добавлено: "{anime.name}"')
        elif resp == 2:
            await callback.answer(f'Нельзя добавить: "{anime.name}". Удалите лишнее из избранного.', show_alert=True)
        elif resp == 0:
            await callback.answer(f'"{anime.name}" уже у Вас в избранном', show_alert=True)

    elif req == 'del':
        resp, anime = await PostgresController().del_user_fav(user_id=user_id, anime_id=anime_id)
        if resp:
            await callback.answer(f'Удалено: "{anime.name}"')
        else:
            await callback.answer(f'"{anime.name}" нет у Вас в избранном', show_alert=True)

    else:
        anime = await PostgresController().get_anime(user_id=user_id, anime_id=anime_id)

    try:
        user_faves = await PostgresController().get_user_faves(user_id=user_id)
        user_fav_check = 1 if anime_id in [x[0].anime_id for x in user_faves] else 0
        await callback.message.edit_reply_markup(reply_markup=await UsersKeyboards.anime_kb(
            anime_id=anime_id, user_fav_check=user_fav_check, url=anime.link))
    except MessageNotModified:
        pass


async def lasts_callback(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    req = callback.data.split('_')[1]
    if req.isdigit():
        try:
            await callback.message.edit_reply_markup(
                reply_markup=await UsersKeyboards.last_kb(user_id=user_id, n=int(req)))
        except MessageNotModified:
            await callback.answer(cache_time=2)


async def today_callback(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    try:
        await callback.message.edit_reply_markup(reply_markup=await UsersKeyboards.today_kb(user_id=user_id))
    except MessageNotModified:
        await callback.answer(cache_time=2)


async def ants_callback(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    try:
        await callback.message.edit_reply_markup(reply_markup=await UsersKeyboards.ants_kb(user_id=user_id))
    except MessageNotModified:
        await callback.answer(cache_time=2)


async def timetable_callback(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    req = callback.data.split('_')[1]
    if req.isdigit():
        return await callback.message.edit_text(f'{DAYS[int(req)][1]}:',
                                                reply_markup=await UsersKeyboards.timetable_day_kb(user_id=user_id,
                                                                                                   day=req))
    elif req == 'all':
        try:
            timetable_str = ''
            timetable_animes = await PostgresController().get_timetable_animes(user_id=user_id, day='all')
            day_count = None
            for item in timetable_animes:
                anime, day, time = item.anime, item.day, item.time
                anime_str = f'\n{anime.name} | {time}'
                if day == day_count:
                    timetable_str += anime_str
                else:
                    day_count = day
                    timetable_str += f'\n\n{DAYS[day][1]}:{anime_str}'

            await callback.message.edit_text(f'Все расписание:\n{timetable_str}',
                                             reply_markup=await UsersKeyboards.timetable_kb(user_id=user_id))
        except MessageNotModified:
            await callback.message.edit_text('Расписание:',
                                             reply_markup=await UsersKeyboards.timetable_kb(user_id=user_id))

    elif req == 'back':
        await callback.message.edit_text('Расписание:', reply_markup=await UsersKeyboards.timetable_kb(user_id=user_id))

    await callback.answer(cache_time=2)


async def find_callback(callback: CallbackQuery, state: FSMContext) -> None:
    user_id = callback.from_user.id
    req = callback.data.split('_')[1]
    if req == 'start':
        await AnimeFind.anime_name.set()
        await callback.message.edit_text(FIND_MSGS['finding'],
                                         reply_markup=await UsersKeyboards.find_cancel_kb(user_id=user_id))
    elif req == 'back':
        await state.finish()
        await callback.message.edit_text(FIND_MSGS['cancel'],
                                         reply_markup=await UsersKeyboards.find_start_kb(user_id=user_id))

    await callback.answer(cache_time=2)


"""Registration handlers"""


async def register_handlers_client(dp: Dispatcher) -> None:
    # Commands
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(fav_command, text=['Избранное'])
    dp.register_message_handler(lasts_command, text=['Последние'])
    dp.register_message_handler(today_command, text=['Сегодня'])

    dp.register_message_handler(ants_command, commands=['ants'])
    dp.register_message_handler(timetable_command, commands=['timetable'])

    dp.register_message_handler(find_command, commands=['find'])
    dp.register_message_handler(finding_anime, state=AnimeFind.anime_name)

    # Callbacks
    dp.register_callback_query_handler(anime_callback, Text(startswith='anime_'))
    dp.register_callback_query_handler(fav_callback, Text(startswith='fav_'))
    dp.register_callback_query_handler(lasts_callback, Text(startswith='last_'))
    dp.register_callback_query_handler(today_callback, Text(startswith='today_'))
    dp.register_callback_query_handler(ants_callback, Text(startswith='ants_'))
    dp.register_callback_query_handler(timetable_callback, Text(startswith='timetable_'))
    dp.register_callback_query_handler(find_callback, Text(startswith='find_'), state='*')
