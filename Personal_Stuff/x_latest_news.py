import feedparser
import pyshorteners
import json
import requests
from pathlib import Path

home = str(Path.home())
t_gram_creds = open((home+'/Desktop/Creds/news_bot.txt'), 'r')
bot_token = t_gram_creds.readline().split('\n')[0]
bot_chatID = t_gram_creds.readline()
t_gram_creds.close()

def shorten(url):
    s = pyshorteners.Shortener()
    return s.tinyurl.short(url)

def telegram_bot_sendtext(bot_message):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

def newspaper_build(url, feed_title):
    message_raw = [feed_title]
    newsfeed_raw = feedparser.parse(url)
    for article in range(len(newsfeed_raw)):
        entry = newsfeed_raw.entries[article]
        publish_date = entry.published
        title = (entry.summary).split('>')[1].split('</a')[0]
        link = shorten(entry.link)
        message_raw.append(f'{publish_date}\n{title}\nMore info: {link}\n\n')
    message = " ".join(message_raw)
    return message

ph_latestnews_url = 'https://news.google.com/rss/search?q=philippines%20latest%20news&hl=en-SG&gl=SG&ceid=SG%3Aen'
ph_latestnews_url_2 = 'https://news.google.com/rss/topics/CAAqHAgKIhZDQklTQ2pvSWJHOWpZV3hmZGpJb0FBUAE/sections/CAQiUENCSVNOam9JYkc5allXeGZkakpDRUd4dlkyRnNYM1l5WDNObFkzUnBiMjV5Q3hJSkwyMHZNREU1TlhCa2Vnc0tDUzl0THpBeE9UVndaQ2dBKjEIACotCAoiJ0NCSVNGem9JYkc5allXeGZkako2Q3dvSkwyMHZNREU1TlhCa0tBQVABUAE?hl=en-SG&gl=SG&ceid=SG%3Aen'
sg_latest_news_url = 'https://news.google.com/rss/search?q=channelnewsasia&hl=en-SG&gl=SG&ceid=SG%3Aen'
macrumors_url = 'https://news.google.com/rss/search?q=macrumors&hl=en-SG&gl=SG&ceid=SG%3Aen'
covid_url = 'https://news.google.com/rss/topics/CAAqIggKIhxDQkFTRHdvSkwyMHZNREZqY0hsNUVnSmxiaWdBUAE?hl=en-SG&gl=SG&ceid=SG%3Aen'
health_fitness_url = 'https://news.google.com/rss/topics/CAAqJQgKIh9DQkFTRVFvSUwyMHZNR3QwTlRFU0JXVnVMVWRDS0FBUAE/sections/CAQiW0NCQVNQZ29JTDIwdk1HdDBOVEVTQldWdUxVZENJZzhJQkJvTENna3ZiUzh3TWpkNE4yNHFHZ29ZQ2hSR1NWUk9SVk5UWDFORlExUkpUMDVmVGtGTlJTQUJLQUEqKQgAKiUICiIfQ0JBU0VRb0lMMjB2TUd0ME5URVNCV1Z1TFVkQ0tBQVABUAE?hl=en-SG&gl=SG&ceid=SG%3Aen'

all = {
    ph_latestnews_url:"PH Latest News\n\n",
    ph_latestnews_url_2:"PH Latest New II\n\n",
    sg_latest_news_url:"SG Latest News\n\n",
    macrumors_url:"Apple News\n\n",
    covid_url:"COVID News\n\n",
    health_fitness_url:"Health/Fitness\n\n"
}

for item in all:
    try:
        news_to_send = newspaper_build(item,all.get(item))
        telegram_bot_sendtext(news_to_send)
    except IndexError as e:
        pass