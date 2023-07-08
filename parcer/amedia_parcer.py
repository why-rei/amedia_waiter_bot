from collections import namedtuple

import requests
from bs4 import BeautifulSoup
from loguru import logger

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/86.0.4240.185 YaBrowser/20.11.2.78 Yowser/2.5 Safari/537.36',
    'accept': '*/*'
}


class AmediaParcer:
    def __init__(self):
        self.url = 'https://amedia.online/'

    @staticmethod
    async def get_page(url: str) -> BeautifulSoup:
        resp = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(resp.text, 'lxml')
        return soup

    async def parce_anime(self, anime_url: str) -> namedtuple:
        soup = await self.get_page(anime_url)
        anime_base = soup.find('article', class_='film-wr')

        anime_id = anime_url.split('-')[0].split('/')[-1]

        anime_name = anime_base.find('h1').text.split('«')[1].split('»')[0]

        try:
            anime_desc = anime_base.find('div', class_='full-text').text.split('                ')[1][:240] + '...'
        except:
            anime_desc = 'Будет позже...'

        anime_info = []
        info = anime_base.find('div', class_='film-info').find_all('div', class_='fi-item')
        for item in info:
            anime_info.append(item.find_next('div', class_='fi-desc').find_next('a').text)
        anime_info = ' | '.join(anime_info)

        anime_photo_url = 'https://amedia.online' + soup.find('div', class_='film-poster').find_next('img').get(
            'data-src')

        Anime = namedtuple('Anime', 'id name info desc photo url')

        return Anime(int(anime_id), anime_name, anime_info, anime_desc, anime_photo_url, anime_url)

    async def parce_home(self):
        soup = await self.get_page(self.url)
        list_animes = soup.find('div', class_='main-section-one').find_all('div', class_='section')

        last_animes = await self.parce_last(list_animes[0])
        today_animes = await self.parce_today(list_animes[1])

        return last_animes, today_animes

    async def parce_last(self, list_animes) -> namedtuple:
        last_animes = list_animes.find_all('div', class_='newser')
        last_animes_list = []
        for anime_ in last_animes:
            anime_url = self.url + anime_.find_next('div', class_='animetitle1').find_next('a').get('href')
            anime_seria = anime_.find_next('div', class_='newseriya').text.split(' ')[0]
            anime_time = anime_.find_next('div', class_='animetitle1').find_next('div', class_='animedata').text

            LastAnime = namedtuple('LastAnime', 'url seria time')

            last_animes_list.append(LastAnime(anime_url, anime_seria, anime_time))

        return last_animes_list

    async def parce_today(self, list_animes) -> namedtuple:
        today_animes = list_animes.find_all('div', class_='newser')
        today_animes_list = []
        for anime_ in today_animes:
            anime_url = self.url + anime_.find_next('div', class_='animetitle1').find_next('a').get('href')
            anime_seria = anime_.find_next('div', class_='newseriya').text.split(' ')[0]
            anime_time = anime_.find_next('div', class_='animetitle1').find_next('div', class_='animedata').text

            TodayAnime = namedtuple('TodayAnime', 'url seria time')

            today_animes_list.append(TodayAnime(anime_url, anime_seria, anime_time))

        return today_animes_list


if __name__ == '__main__':
    import asyncio

    a_url = 'https://amedia.online/1449-geny-iskusstvennogo-intellekta.html'
    res = asyncio.run(AmediaParcer().parce_home())
    print(res[1])
