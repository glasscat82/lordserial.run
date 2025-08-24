import os
from bs4 import BeautifulSoup
from art import tprint
import re
from helper import *


PATH_JSON_FILES = 'json'

def get_ss(text):
    numbers = re.findall(r'\d+', text)
    return [int(x) for x in numbers]

@try_decorator
def get_rating(col_desc):
    """ rating """
    rating = {}
    kp = col_desc.find('div', {'class':'th-rate th-rate-kp'})
    if kp is not None:
        rating['kp'] = float(kp.text.strip())

    imdb = col_desc.find('div', {'class':'th-rate th-rate-imdb'})
    if imdb is not None:
        rating['imdb'] = float(imdb.text.strip())

    return rating

@try_decorator
def get_row(col):
    """ row """
    col_body = col.find('a', {'class':'th-in with-mask'})
    col_series = col_body.find('div', {'class':'th-series'})
    col_desc = col_body.find('div', {'class':'th-desc'})
    col_desc_title = col_desc.find('div', {'class':'th-title'})
    col_th_img = col_body.find('div', {'class':'th-img img-resp-vert'})

    row = {}
    row['url'] = col_body.get("href").strip()

    if col_th_img is not None:
        row['img'] = col_th_img.find('img').get("src").strip()

    if col_desc_title is not None:
        row['title'] = col_desc_title.text.strip()

    if col_series is not None:
        row['series'] = get_ss(col_series.text.strip())

    rating = get_rating(col_desc)

    if rating is not False:
        row = row | rating

    return row

@try_decorator
def get_links(html:str):
    """ links url """
    soup = BeautifulSoup(html, 'lxml')
    selection_main = soup.find('div', {'id':'dle-content'})

    if selection_main is None:
        return False

    links = []
    for col in selection_main.find_all('div', {'class':'th-item'}):
        col_row = get_row(col)
        if col_row is False:
            continue

        links.append(col_row)

    return links

@benchmark
def main(url: str, page:int):
    """ this main """
    for i in range(page):
        p = i + 1
        url_get = f'{url}page/{p}/' if p > 1 else url

        html = get_html(url_get)

        if html is not False:
            links = get_links(html)
            append_json(links, f'./{PATH_JSON_FILES}/{get_file_name()}')
            pc(f'[+] → {p} → {len(links)}', url_get, color = 2)
        else:
            pc(f'[-] 159 → html is False', color = 1)

def get_file_name():
    """ return file name """
    return f'file_{dt.now():%d-%m-%Y_%H}.json'

if __name__ == "__main__":
    """ parsing """
    tprint('.: lordserial.run :.', font='cybermedium')

    if os.path.isdir(PATH_JSON_FILES) is False:
        os.makedirs(f'./{PATH_JSON_FILES}', exist_ok=True)
        pc('[+] created folder', color=3)

    url = f'https://lordserial.run/zarubezhnye-serialy/'
    main(url, 2)