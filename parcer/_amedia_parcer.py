from typing import Type, List, Tuple
from collections import namedtuple

import requests
from bs4 import BeautifulSoup


HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/86.0.4240.185 YaBrowser/20.11.2.78 Yowser/2.5 Safari/537.36',
    'accept': '*/*'
}


class AmediaParcer:
    url = 'https://amedia.online/'

    @staticmethod
    async def get_page(url: str) -> BeautifulSoup:
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'lxml')
            return soup

    async def parce_anime(self, anime_url: str) -> Type[namedtuple]:
        soup = await self.get_page(anime_url)

        if soup:
            anime_base = soup.find('article', class_='film-wr')

            def meta_get(property_: str):
                return soup.find('meta', property=f'{property_}')['content']

            anime_id = anime_url.split('-')[0].split('/')[-1]

            anime_name = meta_get(property_='og:title')

            try:
                anime_desc = meta_get(property_='og:description')
            except TypeError:
                anime_desc = 'Будет позже...'

            anime_info = []
            info = anime_base.find('div', class_='film-info').find_all('div', class_='fi-item')
            for item in info:
                anime_info.append(item.find_next('div', class_='fi-desc').find_next('a').text)
            anime_info = ' | '.join(anime_info)

            anime_photo_url = 'https://amedia.online' + soup.find('div', class_='film-poster').find_next('img').get(
                'data-src')

            Anime = namedtuple('Anime', 'id name info desc photo_url url')

            return Anime(int(anime_id), anime_name, anime_info, anime_desc, anime_photo_url, anime_url)

    async def _parce_last(self, soup_section: BeautifulSoup) -> List[Type[namedtuple]]:
        soup_last_animes = soup_section.find_all('div', class_='newser')
        last_animes = []
        for anime in soup_last_animes:
            anime_url = self.url + anime.find_next('div', class_='animetitle1').find_next('a').get('href')
            anime_seria = anime.find_next('div', class_='newseriya').text.split(' ')[0]
            anime_time = anime.find_next('div', class_='animetitle1').find_next('div', class_='animedata').text

            LastAnime = namedtuple('LastAnime', 'url seria time')

            last_animes.append(LastAnime(anime_url, anime_seria, anime_time))

        return last_animes

    async def _parce_today(self, soup_section: BeautifulSoup) -> List[Type[namedtuple]]:
        soup_today_animes = soup_section.find_all('div', class_='newser')
        today_animes = []
        for anime in soup_today_animes:
            anime_url = self.url + anime.find_next('div', class_='animetitle1').find_next('a').get('href')
            anime_seria = anime.find_next('div', class_='newseriya').text.split(' ')[0]
            anime_time = anime.find_next('div', class_='animetitle1').find_next('div', class_='animedata').text

            TodayAnime = namedtuple('TodayAnime', 'url seria time')
            today_animes.append(TodayAnime(anime_url, anime_seria, anime_time))

        return today_animes

    async def parce_home(self) -> Tuple[Type[namedtuple], Type[namedtuple]]:
        soup = await self.get_page(self.url)
        if soup:
            soup_sections = soup.find('div', class_='main-section-one').find_all('div', class_='section')

            last_animes = await self._parce_last(soup_sections[0])
            today_animes = await self._parce_today(soup_sections[1])

            return last_animes, today_animes

    async def parce_ants(self) -> List[Type[namedtuple]]:
        ants_url = self.url + 'anime-kotoroe-skoro-vyydet/'
        soup = await self.get_page(ants_url)
        if soup:
            ants_animes = soup.find('div', class_='middle-wr').find_all('div', class_='c1-item')
            ants_list = []
            for anime in ants_animes:
                anime_url = anime.find_next('a').get('href')

                AntAnime = namedtuple('AntAnime', 'url')
                ants_list.append(AntAnime(anime_url))
            return ants_list

    async def parce_timetable(self) -> List[Type[namedtuple]]:
        timetable_url = self.url + 'raspisanie-vyhoda-novyh-seriy.html'
        soup = await self.get_page(timetable_url)

        if soup:
            all_timetable = soup.find_all('div', class_='raspis2')

            timetable_list = []
            for day_animes in all_timetable:
                day_animes_list = day_animes.find_all('div', class_='newser')
                for anime in day_animes_list:
                    anime_url = anime.find_next('div', class_='animetitle1').find_next('a').get('href')
                    anime_day = all_timetable.index(day_animes)
                    anime_time = anime.find_next('div', class_='animetitle1').find_next('div', class_='newseriya').text

                    TimetableAnimes = namedtuple('TimetableAnimes', 'url day time')
                    timetable_list.append(TimetableAnimes(anime_url, anime_day, anime_time))

            return timetable_list
