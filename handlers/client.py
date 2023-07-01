from loguru import logger
from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageNotModified, BotBlocked, ChatNotFound

from database.db_controller import db_user_add, db_user_take, db_anime_take, db_favorite_add, db_favorite_delete, \
    db_notice_update_checker, db_timetable_take_all, db_find_anime, db_notice_add, db_notice_take

from handlers.keyboards import kb_main, kb_last_animes, kb_anime, kb_today_animes, kb_favorite, kb_url, kb_ants, \
    kb_timetable, kb_timetable_day, kb_founded

from amedia_parcer import last_today_parce
from create_bot import bot
from data.config import FAVORITE_LIMIT


# Start command
async def start_command(message: Message) -> None:
    user_id = message.from_user.id
    if await db_user_take(user_id) is None:
        await db_user_add(user_id)
    await message.answer('Добавь аниме в избранное и получи уведомление как только оно появится на сайте '
                         'Amedia.online, по любым вопросам - @new_try',
                         reply_markup=kb_main)
    logger.info(user_id)


async def send_anime_callback(callback: CallbackQuery) -> None:
    anime_id = int(callback.data.split('_')[2])
    anime = await db_anime_take(anime_id)
    chat_id = callback.message.chat.id
    await bot.send_photo(chat_id, anime.photo_url, f'{anime.name}\n\n{anime.info}\n\n{anime.desc}',
                         reply_markup=await kb_anime(callback.from_user.id, anime_id))
    await callback.answer(cache_time=2)
    logger.info(callback.from_user.id)


# Last animes
async def last_animes(message: Message) -> None:
    await message.answer('Последние: ', reply_markup=await kb_last_animes(1))
    logger.info(message.from_user.id)


async def last_animes_callback(callback: CallbackQuery) -> None:
    query = callback.data.split('_')[1]
    if query == 'update':
        try:
            await bot.edit_message_text('Последние: ', callback.message.chat.id,
                                        callback.message.message_id, reply_markup=await kb_last_animes(1))
        except MessageNotModified:
            pass
        finally:
            await callback.answer('Обновлено')

    elif query == '0>':
        await bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id,
                                            reply_markup=await kb_last_animes(1))
    elif query == '1>':
        await bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id,
                                            reply_markup=await kb_last_animes(2))
    elif query == '2>':
        await bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id,
                                            reply_markup=await kb_last_animes(3))
    logger.info(callback.from_user.id)


# Today animes
async def today_animes(message: Message) -> None:
    await message.answer('Сегодня: ', reply_markup=await kb_today_animes())
    logger.info(message.from_user.id)


async def today_animes_callback(callback: CallbackQuery) -> None:
    query = callback.data.split('_')[1]
    if query == 'update':
        try:
            await bot.edit_message_text('Сегодня: ', callback.message.chat.id,
                                        callback.message.message_id, reply_markup=await kb_today_animes())
        except MessageNotModified:
            pass
        finally:
            await callback.answer('Обновлено')
    logger.info(callback.from_user.id)


# Favorite
async def favorite(message: Message) -> None:
    user_id = message.from_user.id
    kb_favorite_ = await kb_favorite(user_id)
    fav_msg = 'Избранное: '
    if not kb_favorite_["inline_keyboard"]:
        fav_msg += 'Пусто'
    await message.answer(fav_msg, reply_markup=kb_favorite_)
    logger.info(message.from_user.id)


async def favorite_callback(callback: CallbackQuery) -> None:
    anime_id = int(callback.data.split('_')[2])
    user_id = callback.from_user.id

    query = callback.data.split('_')[1]
    try:
        if query == 'add':
            cb = await db_favorite_add(user_id=user_id, anime_id=anime_id)
            if cb == 'good':
                anime = await db_anime_take(anime_id)
                await callback.answer(f'Добавлено: {anime.name}')
                await bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id,
                                                    reply_markup=await kb_anime(user_id, anime_id))
            elif cb == 'error_already_have':
                await callback.answer('Аниме уже в избранном')
                await bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id,
                                                    reply_markup=await kb_anime(user_id, anime_id))
            elif cb == 'error_limit':
                await callback.answer(f'Превышен лимит избранного ({FAVORITE_LIMIT} аниме), сначала удалите лишнее.',
                                      show_alert=True)
            else:
                await callback.answer('Ошибка при добавлении в избранное, попробуйте снова')

        elif query == 'delete':
            cb = await db_favorite_delete(user_id=user_id, anime_id=anime_id)
            if cb == 'good':
                await callback.answer('Аниме удалено из избранного')
                await bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id,
                                                    reply_markup=await kb_anime(user_id, anime_id))
            elif cb == 'bad':
                await callback.answer('Ошибка при удалении из избранного')
                await bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id,
                                                    reply_markup=await kb_anime(user_id, anime_id))
    except MessageNotModified:
        pass
    logger.info(callback.from_user.id)


# Ants
async def ants(message: Message) -> None:
    await message.answer('Анонсы: ', reply_markup=await kb_ants())
    logger.info(message.from_user.id)


# Timetable
async def timetable(message: Message) -> None:
    await message.answer('Расписание: ', reply_markup=await kb_timetable())
    logger.info(message.from_user.id)


# Finder
class AnimeFind(StatesGroup):
    anime_name = State()


async def find_anime(message: Message) -> None:
    await AnimeFind.anime_name.set()
    await message.answer('Введите название аниме (Соблюдайте регистр букв, как на сайте):')
    logger.info(message.from_user.id)


async def finding_anime(message: Message, state: FSMContext) -> None:
    await state.update_data(anime_name=message.text)
    user_data = await state.get_data()
    anime_name_finding = user_data["anime_name"]
    animes_ids_list = await db_find_anime(anime_name_finding)
    await bot.send_message(message.chat.id, 'Найдено: ', reply_markup=await kb_founded(animes_ids_list))
    await state.finish()
    logger.info(f'{message.from_user.id} try: "{anime_name_finding}"')


async def timetable_callback(callback: CallbackQuery) -> None:
    day = callback.data.split('_')[1]
    if day == 'back':
        await bot.edit_message_text('Расписание: ', callback.message.chat.id, callback.message.message_id,
                                    reply_markup=await kb_timetable())
    elif day == 'all':
        timetable_msg = await db_timetable_take_all()
        await bot.send_message(callback.from_user.id, timetable_msg)
        await callback.answer(cache_time=1)
    elif day == '0':
        await bot.edit_message_text('Понедельник: ', callback.message.chat.id, callback.message.message_id,
                                    reply_markup=await kb_timetable_day(day))
    elif day == '1':
        await bot.edit_message_text('Вторник: ', callback.message.chat.id, callback.message.message_id,
                                    reply_markup=await kb_timetable_day(day))
    elif day == '2':
        await bot.edit_message_text('Среда: ', callback.message.chat.id, callback.message.message_id,
                                    reply_markup=await kb_timetable_day(day))
    elif day == '3':
        await bot.edit_message_text('Четверг: ', callback.message.chat.id, callback.message.message_id,
                                    reply_markup=await kb_timetable_day(day))
    elif day == '4':
        await bot.edit_message_text('Пятница: ', callback.message.chat.id, callback.message.message_id,
                                    reply_markup=await kb_timetable_day(day))
    elif day == '5':
        await bot.edit_message_text('Суббота: ', callback.message.chat.id, callback.message.message_id,
                                    reply_markup=await kb_timetable_day(day))
    elif day == '6':
        await bot.edit_message_text('Воскресение: ', callback.message.chat.id, callback.message.message_id,
                                    reply_markup=await kb_timetable_day(day))
    logger.info(callback.from_user.id)


# Notice
@logger.catch()
async def notice_and_main_parce() -> None:
    await last_today_parce()
    await db_notice_add()
    # notice sys
    try:
        notice_list = await db_notice_take()
        if notice_list:
            for notice_item in notice_list:
                anime = notice_item[0]
                anime_id = anime.id
                anime_seria = notice_item[1]
                users_ids_list = notice_item[2]

                notice_msg = f'Вышла {anime_seria} серия «{anime.name}»'
                kb_url_ = await kb_url(anime.link)
                for user_id in users_ids_list:
                    try:
                        await bot.send_photo(user_id[0], anime.photo_url, notice_msg, reply_markup=kb_url_)
                    except Exception as e:
                        logger.warning(e)
                await db_notice_update_checker(anime_id=anime_id, anime_seria=anime_seria)
                logger.info(f'id: {anime_id} name: {anime.name} seria: {anime_seria}')
    except Exception as e:
        logger.exception(e)
    logger.info('')


async def register_handlers_client(dp: Dispatcher) -> None:
    # Commands
    dp.register_message_handler(start_command, commands=['start'])

    dp.register_message_handler(last_animes, text=['Последние'])
    dp.register_message_handler(today_animes, text=['Сегодня'])
    dp.register_message_handler(favorite, text=['Избранное'])

    dp.register_message_handler(find_anime, commands=['find'], state=None)
    dp.register_message_handler(finding_anime, state=AnimeFind.anime_name)

    dp.register_message_handler(ants, commands=['ants'])
    dp.register_message_handler(timetable, commands=['timetable'])

    # Callbacks
    dp.register_callback_query_handler(last_animes_callback, Text(startswith='last_'))
    dp.register_callback_query_handler(today_animes_callback, Text(startswith='today_'))
    dp.register_callback_query_handler(favorite_callback, Text(startswith='fav_'))
    dp.register_callback_query_handler(send_anime_callback, Text(startswith='send_anime_'))
    dp.register_callback_query_handler(timetable_callback, Text(startswith='timetable_'))
