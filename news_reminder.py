import pandas as pd
import datetime
from datetime import datetime, timedelta
from pathlib import Path
import requests
from check_news import *
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
port = 1122 #FXCM MAIN 50k 1:100
list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair
con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup=symbols)

if 22 < datetime.now().hour < 5: #do not run between 10pm - 5am
    exit()

def pair_name(currency):
    symbol_dict = {'g':'GBP', 'j':'JPY', 'u':'USD','c':'CAD', 
    'f':'CHF','e':'EUR', 'a':'AUD', 'x':'XAU', 'n':'NZD'}
    first = symbol_dict[list(currency)[0]]
    second = symbol_dict[list(currency)[1]]
    fx_currency = first + second
    return fx_currency

def telegram_bot_sendtext(bot_message):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

home = str(Path.home())

t_gram_creds = open((home+'/Desktop/t_gram.txt'), 'r')
bot_token = t_gram_creds.readline().split('\n')[0]
bot_chatID = t_gram_creds.readline()
t_gram_creds.close()

curr_to_avoid_raw =[]
fx_calendar = pd.read_csv(home+'\Desktop\Fx_calendar_2b_raw.csv')
today = datetime.now()
curr_to_avoid_time = fx_calendar[['Currency', 'Converted']][(fx_calendar['Date']==today.strftime('%m/%d/%Y')) & (fx_calendar['Time']>today.strftime('%H:%M'))]
curr_to_avoid_time.reset_index(inplace=True)
curr_to_avoid_time.drop(columns = ['index'],inplace=True)
for line in curr_to_avoid_time['Converted']:
    test = datetime.now() + timedelta(minutes = 30) <= datetime.strptime(line, '%m/%d/%Y %H:%M') <= datetime.now() + timedelta(minutes = 30) #OG algo
    if test == True:
        curr_to_avoid_raw.append(curr_to_avoid_time['Currency'][curr_to_avoid_time['Converted'] == line].values[0])

curr_to_avoid_raw = list(set(curr_to_avoid_raw))
if len(curr_to_avoid_raw) == 0:
    telegram_bot_sendtext('No upcoming news.')
    exit()

positions = MT.Get_all_open_positions()
with_position = set(list(positions['instrument']))
with_position = list(with_position)

if len(with_position) == 0:
    telegram_bot_sendtext('No upcoming news for opened positions.')
    exit()

for pair in with_position:
    validation, events = check_news(pair)
    if validation == True:
        telegram_bot_sendtext('ALERT! ', pair, ' has upcoming news.', str(events))
    else:
        telegram_bot_sendtext('No upcoming news on opened positions.')