from collections import namedtuple

from aiogram.utils.exceptions import Unauthorized

from core.settings import bot
from data import NOTICE_MSG
from databases import PostgresNotice, MongoNotice, PostgresUsers
from handlers.keyboards import NoticesKeyboards


class NoticeSys:
    @staticmethod
    async def _update_notice_table():
        last_animes = await PostgresNotice.get_all_last_animes()
        notice_animes = []
        for item in last_animes:
            anime_id = item[0].anime_id
            anime_seria = item[0].seria

            notice_check = await PostgresNotice.check_notice(anime_id=anime_id, anime_seria=anime_seria)
            if not notice_check:
                NoticeAnime = namedtuple('NoticeAnime', 'id seria')
                notice_animes.append(NoticeAnime(anime_id, anime_seria))

        await PostgresNotice.update_notice(notice_animes)

    @staticmethod
    async def _create_notice():
        notices = await PostgresNotice.get_notices()
        for item in notices:
            notice_id = item[0].id
            anime_id = item[0].anime_id
            anime_seria = item[0].seria
            users = await PostgresNotice.get_users_favorites(anime_id=anime_id)
            users = [x[0] for x in users]
            await MongoNotice().create_notice(notice_id=notice_id, anime_id=anime_id,
                                              anime_seria=anime_seria, users=users)

    @staticmethod
    async def _send_notice(notice: dict):
        _id = notice['_id']

        anime_id = notice['anime_id']
        anime_seria = notice['anime_seria']
        users = notice['users']
        if users:
            anime = await PostgresNotice.get_anime(anime_id=anime_id)
            for user in users:
                if user['got'] == 0:
                    user_id = user['user_id']
                    notice_msg = NOTICE_MSG.format(anime_seria=anime_seria, anime_name=anime.name)
                    try:
                        await bot.send_photo(chat_id=user_id, photo=anime.photo_url, caption=notice_msg,
                                             reply_markup=await NoticesKeyboards.notice_kb(anime_url=anime.link))

                        await MongoNotice.set_user_got(_id=_id, user_id=user_id)
                        await PostgresUsers().mark_user(user_id=user_id)
                    except Unauthorized:
                        await MongoNotice.set_user_got(_id=_id, user_id=user_id)

    async def _send_notices(self):
        notices = await MongoNotice.get_notices()
        if notices:
            async for notice in notices:
                await self._send_notice(notice=notice)
                await PostgresNotice.turn_notice_checker(notice_id=notice['notice_id'])
                await MongoNotice.delete_notice(_id=notice['_id'])

    async def notice(self):
        await self._update_notice_table()
        await self._create_notice()
        await self._send_notices()
