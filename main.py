#!/usr/bin/python3

import configparser
import requests
import telepot
from bs4 import BeautifulSoup

# Webpage to monitor
url = 'https://www.sec.gov/rules/sro/batsbzx.htm'

# Import config
config = configparser.ConfigParser()
config.read('config.ini')
telegram_user = config['TELEGRAM']['USERS']
telegram_token = config['TELEGRAM']['TOKEN']

# File to store old news in
file = 'old_news.txt'

def cryptobuddy_bot(message):
    """ Sends new items using Telegram """
    bot = telepot.Bot(telegram_token)
    bot.sendMessage(telegram_user, message)

def read_generic():
    """ Reads specified text file into list, stripping out newline characters, and returns it """
    f = open(file, 'r')
    text = f.readlines()
    f.close()
    result = []
    for t in text:
        result.append(t.rstrip('\n'))
    return result

def write_generic(data):
    """ Writes any new items to textfile on new line """
    f = open(file, 'a')
    f.write(data)
    f.write('\n')
    f.close()

def checkETF():
    """Checks sec.gov for any bitcoin related updates"""
    # Get URL and parse with BeautifulSoup
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
    r = requests.get(url, allow_redirects=True, headers=headers)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')

    # Extract all listed items on the page
    tagged_values = soup.find_all("b", class_='blue')
    scraped_items = [x.get_text() for x in tagged_values]

    # Remove duplicate entries in scraped_items
    scraped_clean = list(set(scraped_items))

    # Check against our list of keywords and database of old items
    old_news = read_generic()
    hitlist = []
    keywords = ['bitcoin', 'coin', 'crypto', 'xbt', 'btc', 'winklevoss']
    for keyword in keywords:
        for item in scraped_clean:
            if keyword in item.lower():  # remove all capitalization to make matching easier
                if item not in hitlist and item not in old_news:
                        hitlist.append(item)

    # Send any new items using Telegram and store it in database
    if hitlist:
        for hit in hitlist:
            cryptobuddy_bot(hit)  # Send using Telegram
            write_generic(hit)  # Store in database

            # Find the links associated with the new items found
            hitlink = soup.find(text=hit)
            link_short = hitlink.findPrevious('a')
            link_full = 'https://www.sec.gov' + link_short.get('href')
            cryptobuddy_bot(link_full)

checkETF()