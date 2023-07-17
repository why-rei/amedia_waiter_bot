from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from aiogram.utils.exceptions import MessageNotModified
from loguru import logger

from core.settings import bot
from handlers.keyboards import UsersKeyboards
from databases import PostgresController
from data import START_MESSAGE

"""Messages handlers"""


async def start_command(message: Message) -> None:
    user_id = message.from_user.id
    await PostgresController().add_user(user_id=user_id)
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
        if resp:
            await callback.answer(f'Добавлено: "{anime.name}"')
        else:
            await callback.answer(f'"{anime.name}" уже у Вас в избранном', show_alert=True)
        try:
            await callback.message.edit_reply_markup(reply_markup=await UsersKeyboards.anime_kb(anime_id=anime_id,
                                                                                                user_fav_check=1,
                                                                                                url=anime.link))
        except MessageNotModified:
            pass
    elif req == 'del':
        resp, anime = await PostgresController().del_user_fav(user_id=user_id, anime_id=anime_id)
        if resp:
            await callback.answer(f'Удалено: "{anime.name}"')
        else:
            await callback.answer(f'"{anime.name}" нет у Вас в избранном', show_alert=True)
        try:
            await callback.message.edit_reply_markup(reply_markup=await UsersKeyboards.anime_kb(anime_id=anime_id,
                                                                                                user_fav_check=0,
                                                                                                url=anime.link))
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


"""Registration handlers"""


async def register_handlers_client(dp: Dispatcher) -> None:
    # Commands
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(fav_command, text=['Избранное'])
    dp.register_message_handler(lasts_command, text=['Последние'])
    dp.register_message_handler(today_command, text=['Сегодня'])

    dp.register_message_handler(ants_command, commands=['ants'])

    # Callbacks
    dp.register_callback_query_handler(anime_callback, Text(startswith='anime_'))
    dp.register_callback_query_handler(fav_callback, Text(startswith='fav_'))
    dp.register_callback_query_handler(lasts_callback, Text(startswith='last_'))
    dp.register_callback_query_handler(today_callback, Text(startswith='today_'))
    dp.register_callback_query_handler(ants_callback, Text(startswith='ants_'))
