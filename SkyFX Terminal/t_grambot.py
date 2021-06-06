#telegram_bot
import requests
from pathlib import Path
home = str(Path.home())

def get_tcreds():
    creds = {}
    t_gram_creds = open((home+'/Desktop/t_gram.txt'), 'r')
    bot_token = t_gram_creds.readline().split('\n')[0]
    bot_chatID = t_gram_creds.readline()
    creds['bot_token'] = bot_token
    creds['bot_chatID'] = bot_chatID
    t_gram_creds.close()
    return creds

def telegram_bot_sendtext(bot_message):
    send_text = 'https://api.telegram.org/bot' + get_tcreds()['bot_token'] + '/sendMessage?chat_id=' + get_tcreds()['bot_chatID'] + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

def telegram_bot_sendfile(filename):
    url = "https://api.telegram.org/bot" + get_tcreds()['bot_token'] + "/sendDocument"
    files = {'document': open((home +'\Desktop' + '\/' + filename), 'rb')}
    data = {'chat_id' : get_tcreds()['bot_chatID']}
    r= requests.post(url, files=files, data=data)
    return r.status_code, r.reason, r.content
