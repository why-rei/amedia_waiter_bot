import requests
from bs4 import BeautifulSoup
from loguru import logger

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/86.0.4240.185 YaBrowser/20.11.2.78 Yowser/2.5 Safari/537.36',
    'accept': '*/*'
}
