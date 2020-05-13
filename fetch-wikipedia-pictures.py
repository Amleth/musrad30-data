from bs4 import BeautifulSoup
import pandas
import requests
from os import path

for id, row in pandas.read_excel("2020-04-18 musiciens_séparés virgules et complétés wiki par cb.xlsx", sheet_name="musiciens_complété par cb", encoding='utf-8').iterrows():
    if not pandas.isna(row['URL page wikipedia']):
        already_downloaded = False
        for pic_ext in ['gif', 'GIF', 'jpg', 'JPG', 'jpeg', 'JPEG', 'png', 'PNG']:
            if path.exists('wikipedia-pictures/' + str(row['IDmusiciens']) + '.' + pic_ext):
                already_downloaded = True
                break
        if already_downloaded:
            continue
        print(row['URL page wikipedia'])
        page = requests.get(row['URL page wikipedia'])
        soup = BeautifulSoup(page.content, 'html.parser')

        results = soup.find('div', {"class": "infobox_v3"})
        if results == None:
            results = soup.find('table', {"class": "infobox"})
        if results == None:
            results = soup.find('div', {"class": "thumbinner"})
        if results == None:
            results = soup.find('table', {"class": "infobox_v2"})
        if results == None:
            continue
        results = results.findAll('img')
        if len(results) == 0:
            continue
        results = results[0]['src']
        pic_url = 'http:' + results
        pic_ext = pic_url.split('.')[-1]
        f = open('wikipedia-pictures/' + str(row['IDmusiciens']) + '.' + pic_ext, 'wb')
        f.write(requests.get(pic_url).content)
        f.close()
        print('->', str(row['IDmusiciens']) + '.' + pic_ext)
