import logging
import re
import requests
import htmlmin
from bs4 import BeautifulSoup


def ce_get_list(url):
    try:
        r = requests.get(url)
        r.encoding ='utf-8'
        bs = BeautifulSoup(r.text, 'html.parser')

        article_list = []

        for x in bs.find_all('td', class_='subject'):
            for link in x.find_all('a'): 
                current_article_link = "https://ce.daegu.ac.kr/hakgwa_home/ce/sub.php" + link.get('href')
                current_article_title = x.get_text().strip()
                article_list.append([current_article_title, current_article_link])
        return article_list

    except Exception as e:
        logging.error(e)
        return []