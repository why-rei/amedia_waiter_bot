import requests
from bs4 import BeautifulSoup
from loguru import logger

from database.db_controller import db_anime_add, db_anime_check, db_anime_last_add, db_anime_today_add, \
    db_ants_update, db_timetable_update

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/86.0.4240.185 YaBrowser/20.11.2.78 Yowser/2.5 Safari/537.36',
    'accept': '*/*'
}


async def anime_parce_add(url):
    a_resp = requests.get(url, headers=HEADERS)
    a_soup = BeautifulSoup(a_resp.text, 'lxml')
    a_base = a_soup.find('article', class_='film-wr')

    anim_id = url.split('-')[0].split('/')[-1]
    anim_name = a_base.find('h1').text.split('«')[1].split('»')[0]
    anim_desc = 'Будет позже...'
    try:
        anim_desc = a_base.find('div', class_='full-text').text.split('                ')[1][:240] + '...'
    except:
        pass
    anim_info_ = []
    info = a_base.find('div', class_='film-info').find_all('div', class_='fi-item')
    for item in info:
        anim_info_.append(item.find_next('div', class_='fi-desc').find_next('a').text)
    anim_info = ' | '.join(anim_info_)
    anim_photo_url = 'https://amedia.online' + a_soup.find('div', class_='film-poster').find_next('img').get(
        'data-src')

    await db_anime_add(int(anim_id), anim_name, anim_desc, anim_info, url, anim_photo_url)


async def one_time_parce() -> None:
    try:
        for page_num in range(105, 0, -1):
            try:
                print(page_num)
                url = f'https://amedia.online/anime/page/{page_num}/'
                response = requests.get(url, headers=HEADERS)
                soup = BeautifulSoup(response.text, 'lxml')
                a_list = soup.find('div', id='dle-content').find_all('div', class_='c1-item')
                a_url_list = []
                for a in a_list:
                    a_url = a.find_next('a', class_='c1-img').get('href')
                    a_url_list.append(a_url)

                # Anime page
                for a_url in a_url_list:
                    await anime_parce_add(a_url)
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)


@logger.catch()
async def last_today_parce() -> None:
    url = 'https://amedia.online'
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'lxml')

    animes = soup.find('div', class_='main-section-one').find_all('div', class_='section')

    animes_last = animes[0].find_all('div', class_='newser')

    anime_last_list = []
    for anime in animes_last:
        anim_half_href = anime.find_next('div', class_='animetitle1').find_next('a').get('href')
        anim_id = int(anim_half_href.split('-')[0].replace('/', ''))

        if await db_anime_check(anim_id):
            a_url = 'https://amedia.online' + anim_half_href
            await anime_parce_add(a_url)

        anim_seria = anime.find_next('div', class_='newseriya').text.split(' ')[0]
        anim_time = anime.find_next('div', class_='animetitle1').find_next('div', class_='animedata').text

        anime_last_list.append((anim_id, anim_seria, anim_time))
    await db_anime_last_add(anime_last_list)

    animes_today = animes[1].find_all('div', class_='newser')

    anime_today_list = []
    for anime in animes_today:
        anim_half_href = anime.find_next('div', class_='animetitle1').find_next('a').get('href')
        anim_id = int(anim_half_href.split('-')[0].replace('/', ''))

        if await db_anime_check(anim_id):
            a_url = 'https://amedia.online' + anim_half_href
            await anime_parce_add(a_url)

        anim_seria = anime.find_next('div', class_='newseriya').text.split(' ')[0]
        anim_time = anime.find_next('div', class_='animetitle1').find_next('div', class_='animedata').text

        anime_today_list.append((anim_id, anim_seria, anim_time))
    await db_anime_today_add(anime_today_list)


@logger.catch()
async def ants_parce() -> None:
    url = 'https://amedia.online/anime-kotoroe-skoro-vyydet/'
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'lxml')
    animes = soup.find('div', class_='middle-wr').find_all('div', class_='c1-item')
    ants_list = []
    for anime in animes:
        anime_href = anime.find_next('a').get('href')
        anime_id = int(anime_href.split('-')[0].split('/')[-1])
        anime_name = anime.find_next('div', class_='c1-title').text

        await anime_parce_add(anime_href)
        ants_list.append((anime_id, anime_name))
    await db_ants_update(ants_list)
    logger.info('')


@logger.catch()
async def timetable_parce() -> None:
    url = 'https://amedia.online/raspisanie-vyhoda-novyh-seriy.html'
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'lxml')
    all_timetable = soup.find_all('div', class_='raspis2')

    timetable_list = []
    for day_animes in all_timetable:
        day_animes_list = day_animes.find_all('div', class_='newser')
        for anime in day_animes_list:
            anime_url = anime.find_next('div', class_='animetitle1').find_next('a').get('href')
            anime_id = int(anime_url.split('-')[0].split('/')[-1])
            anime_day = all_timetable.index(day_animes)
            anime_time = anime.find_next('div', class_='animetitle1').find_next('div', class_='newseriya').text

            await anime_parce_add(anime_url)

            timetable_list.append((anime_id, str(anime_day), str(anime_time)))
    await db_timetable_update(timetable_list)
    logger.info('')


if __name__ == '__main__':
    import asyncio

    asyncio.run(last_today_parce())
