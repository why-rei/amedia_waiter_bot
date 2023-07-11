from collections import namedtuple
from typing import Type, List, Sequence

from parcer import AmediaParcer
from databases.postgres_controller import PostgresController


class ParcerConn:

    @staticmethod
    async def _get_anime_id(anime_url: str) -> int:
        anime_id = int(anime_url.split('/')[-1].split('-')[0])
        return anime_id

    async def _get_all_animes_ids(self, animes: Sequence[Type[namedtuple]]) -> List[int]:
        animes_ids_list = []
        for anime in animes:
            anime_id = await self._get_anime_id(anime_url=anime.url)
            animes_ids_list.append(anime_id)
        return animes_ids_list

    @staticmethod
    async def _get_anime(anime_url: str) -> Type[namedtuple]:
        anime = await AmediaParcer().parce_anime(anime_url=anime_url)
        return anime

    async def _push_anime(self, anime_url: str) -> None:
        pk, name, info, desc, photo_url, url = await self._get_anime(anime_url=anime_url)
        await PostgresController().add_anime(pk=pk, name=name, info=info, desc=desc, photo_url=photo_url, url=url)

    async def _initialize_animes(self, animes: Sequence[Type[namedtuple]]):
        animes_ids = await self._get_all_animes_ids(animes=animes)
        unidentified_indexes = await PostgresController().check_animes_ids(animes_ids=animes_ids)
        if unidentified_indexes:
            for index in unidentified_indexes:
                anime_url = animes[index].url
                await self._push_anime(anime_url=anime_url)

    async def _allocation_animes(self, animes: Sequence[Type[namedtuple]]) -> None:
        await self._initialize_animes(animes=animes)

        for anime in animes:
            namedtuple_name = anime.__class__.__name__
            match namedtuple_name:
                case 'LastAnime':
                    # 1. Get all ids list
                    # 2. Check ids list
                    # 3. if not id -> add anime
                    # 4. update last animes table
                    pass

    async def update_main(self):
        last_animes, today_animes = await AmediaParcer().parce_home()
        await self._allocation_animes(last_animes)
        # get(last, today) -> check & add(db animes) ->  db(last & today)


if __name__ == '__main__':
    import asyncio

    r = asyncio.run(ParcerConn().update_main())
    print(r)
