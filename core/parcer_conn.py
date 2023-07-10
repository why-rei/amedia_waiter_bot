from collections import namedtuple
from typing import Iterable

from parcer import AmediaParcer


class ParcerConn:

    @staticmethod
    async def _get_anime_id(anime_url: str) -> int:
        anime_id = int(anime_url.split('/')[-1].split('-')[0])
        return anime_id

    async def _initialize_animes(self, animes: Iterable[namedtuple]) -> None:
        for anime in animes:
            namedtuple_name = anime.__class__.__name__
            match namedtuple_name:
                case 'LastAnime':
                    print(anime)

    async def update_main(self):
        last_animes, today_animes = await AmediaParcer().parce_home()
        await self._initialize_animes(last_animes)
        # get(last, today) -> check & add(db animes) ->  db(last & today)


if __name__ == '__main__':
    import asyncio

    r = asyncio.run(ParcerConn().update_main())
    print(r)
