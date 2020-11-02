import sys
import time
import random
import requests
from datetime import date
from datetime import timedelta
from collections import defaultdict
from bs4 import BeautifulSoup

url_format = 'https://www.billboard.com/charts/hot-100/%02d-%02d-%02d'

def sleep():
    time.sleep(random.uniform(2, 5))

def gen_urls(y):
    num_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if y % 4 == 0 and y % 100 != 0:
        num_days[1] += 1
    urls = []
    for i in range(12):
        for j in range(num_days[i]):
            if date(y, i + 1, j + 1).weekday() == 5 and date(y, i + 1, j + 1) <= date.today() + timedelta(days=6):
                urls.append(url_format%(y, i + 1, j + 1))
    return urls

song_scores = defaultdict(int)

def process_page(url, mode):
    response = requests.get(url)
    page = BeautifulSoup(response.content, 'html.parser')
    songs = page.find_all('button', class_='chart-element__wrapper')
    if len(songs) != 100:
        print(len(songs))
        print('ran into page issue')
        with open('log.txt', 'w+') as f:
            f.write(str(page))
        sys.exit(0)

    for song in songs:
        points = 100 / float(song.find_all('span', class_='chart-element__rank__number')[0].text)
        title = song.find_all('span', class_='chart-element__information__song')
        artist = song.find_all('span', class_='chart-element__information__artist')
        song_name = str(title[0].text).strip()
        song_artist = str(artist[0].text).strip()
        assert('##########' not in song_name)
        song_id = song_name + '##########' + song_artist
        if mode == 'Before':
            if song_id in song_scores:
                song_scores.pop(song_id)
            continue
        if mode == 'After' and not song_id in song_scores:
            continue
        song_scores[song_id] += points

if __name__ == '__main__':
    year = int(sys.argv[1])
    urls = gen_urls(year)
    for u in urls:
        print('processing %s'%(u), end='\r')
        process_page(u, 'Main')
        sleep() # to avoid triggering CAPTCHA
    urls = gen_urls(year - 1)
    urls.reverse()
    for u in urls:
        print('processing %s'%(u), end='\r')
        process_page(u, 'Before')
        sleep() # to avoid triggering CAPTCHA
    urls = gen_urls(year + 1)
    for u in urls:
        print('processing %s'%(u), end='\r')
        process_page(u, 'After')
        sleep() # to avoid triggering CAPTCHA
    print('DONE' + ' '*50)

    with open('top_songs_%s.txt'%(year), 'w+') as song_file:
        for a in sorted(song_scores, key=(lambda x : -song_scores[x]))[:100]:
            song_file.write('%s - %s\n'%tuple(a.split('##########')))
