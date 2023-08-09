import asyncio
import multiprocessing

import requests
from bs4 import BeautifulSoup

from parcer import ParcerConn

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/86.0.4240.185 YaBrowser/20.11.2.78 Yowser/2.5 Safari/537.36',
    'accept': '*/*'
}

ANIMES_URL = 'https://amedia.online/anime/page/'


def get_page(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, 'lxml')
        return soup
    else:
        print(f'{resp.status_code}')


def get_count_pages(soup) -> int:
    if soup:
        r = soup.find('div', id='dle-content').find_next('div', class_='bottom-nav'). \
            find_next('span', class_='navigation').find_all('a')[-1].text
        return int(r)


async def parce_page(page_num: int):
    page_url = ANIMES_URL + str(page_num)
    page_soup = get_page(page_url)
    animes_items = page_soup.find('div', id='dle-content').find_all('div', class_='c1-item')
    for anime_item in animes_items:
        anime_url = anime_item.find_next('a').get('href')
        await ParcerConn()._push_anime(anime_url=anime_url)

        print(f'[INFO]\t{page_num=}\t:\t{anime_url=}')


def main(page_num: int):
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(parce_page(page_num=page_num))


if __name__ == '__main__':
    first_page_soup = get_page(ANIMES_URL + '1')
    count_pages = get_count_pages(first_page_soup)

    with multiprocessing.Pool(multiprocessing.cpu_count() * 3) as pool:
        pool.map(main, list(range(1, count_pages + 1)))
        pool.close()
        pool.join()
