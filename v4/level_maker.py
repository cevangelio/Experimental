#level maker every 5am M-F

#SkyCE FX 3.0 Watchlist maker

from datetime import datetime
import pandas as pd
import time
from pathlib import Path
import finnhub
import requests
import numpy as np

api_key = 'c1iobuf48v6vit2166cg'
finnhub_client = finnhub.Client(api_key=api_key)

if datetime.now().weekday() > 4: #don't run on weekends
    exit()
elif datetime.now().weekday() == 0 and datetime.now().hour < 5: #run only when market opens on Monday 5am
    exit()
else:
    pass

home = str(Path.home())

t_gram_creds = open((home+'/Desktop/t_gram.txt'), 'r')
bot_token = t_gram_creds.readline().split('\n')[0]
bot_chatID = t_gram_creds.readline()
t_gram_creds.close()


def telegram_bot_sendtext(bot_message):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

def telegram_bot_sendfile(filename, location):
    url = "https://api.telegram.org/bot" + bot_token + "/sendDocument"
    files = {'document': open((location+filename), 'rb')}
    data = {'chat_id' : bot_chatID}
    r= requests.post(url, files=files, data=data)
    print(r.status_code, r.reason, r.content)

def pair_name(currency):
    symbol_dict = {'g':'GBP', 'j':'JPY', 'u':'USD','c':'CAD', 
    'f':'CHF','e':'EUR', 'a':'AUD', 'x':'XAU', 'n':'NZD'}
    first = symbol_dict[list(currency)[0]]
    second = symbol_dict[list(currency)[1]]
    fx_currency = first + second
    return fx_currency

def slice_pair(pair):
    sliced = []
    sliced.append(pair[:3])
    sliced.append(pair[3:6])
    return sliced

def symbol_maker(pair):
    if len(pair) != 6:
        return "Error. Not a valid pair."
    else:
        final = "OANDA:" + pair[:3].upper() + "_" + pair[3:6].upper()
        return final

def get_sr(symbol,tf=240):
    '''
    tf = 1, 5, 15, 30, 60, D, W, M

    '''
    symbol = symbol_maker(symbol)
    try:
        raw = requests.get('https://finnhub.io/api/v1/scan/support-resistance?symbol='+symbol+'&resolution='+str(tf)+'&token='+api_key)
        levels = raw.json()['levels']
        return levels
    except:
        print("Error: Check arguments.")


fx_pairs = []
fx_raw =  ['ac', 'af', 'aj', 'an', 'au', 'cf', 'cj', 'ea', 'ec', 'ef', 'eg', 'ej', 'eu', 'fj', 'ga', 'gf', 'gj', 'gu', 'nc', 'nj', 'nu', 'uc', 'uf', 'uj']
for pair in fx_raw:
    fx_pairs.append(pair_name(pair))

df_pairs = pd.DataFrame()
df_pairs['Currency'] = fx_pairs

levels = []
for currency in df_pairs['Currency']:
    sr = get_sr(currency, 240)
    levels.append(sr)
    print('SR done: ' + currency)
    time.sleep(2)

df_pairs['Levels'] = levels

df_pairs.to_csv(home + '/Desktop/Experimental/v3/levels.csv', index = False)
filename = 'levels.csv'
location = home + '/Desktop/Experimental/v3/'
telegram_bot_sendfile(filename=filename, location=location)
telegram_bot_sendtext('Saved levels.')   
print('Done.')