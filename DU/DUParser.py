import logging
import re
import requests
import htmlmin
from bs4 import BeautifulSoup


def ce_get_list(url,content):
    try:
        r = requests.get(url+content)
        r.encoding ='utf-8'
        bs = BeautifulSoup(r.text, 'html.parser')

        article_list = []

        for x in bs.find_all('td', class_='subject'):
            for link in x.find_all('a'): 
                current_article_link = url + link.get('href')
                current_article_title = x.get_text().strip()
                article_list.append([current_article_title, current_article_link])
        return article_list

    except Exception as e:
        logging.error(e)
        return []