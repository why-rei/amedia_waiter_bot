from collections import namedtuple

from databases import PostgresNotice


async def update_notice():
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


if __name__ == '__main__':
    import asyncio

    asyncio.run(update_notice())
