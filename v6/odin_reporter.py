import pandas as pd
from pytz import timezone
import pytz
import requests
import datetime
from datetime import date, datetime, timedelta, tzinfo
from pathlib import Path
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
ports = [1122, 1125, 1127, 1129, 1131]
port_dict = {1122:'FTMO_Live', 1125:'FXCM_Demo', 1127:'GP_Live', 1129:'GP_Demo', 1131:'FTMO_Demo'}

if datetime.now().weekday() > 4: #don't run on weekends
    exit()
else:
    pass

# list_symbols = ['AUDCAD','AUDUSD','EURUSD', 'GBPUSD','NZDUSD','USDCAD','USDCHF','USDJPY'] #2021 best performing
list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCAD','GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair

con = MT.Connect(server='127.0.0.1', port=1125, instrument_lookup=symbols)

home = str(Path.home())
t_gram_creds = open((home+'/Desktop/t_gram.txt'), 'r')
bot_token = t_gram_creds.readline().split('\n')[0]
bot_chatID = t_gram_creds.readline()
t_gram_creds.close()
timezone = pytz.timezone("Etc/UTC")


def telegram_bot_sendtext(bot_message):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

morning_raw = MT.Get_closed_positions_within_window(date_from=datetime(date.today().year,date.today().month,date.today().day, tzinfo=timezone), date_to=datetime.now())
print(morning_raw)
morning_profit = morning_raw['profit'].sum()
print(morning_profit)

if len(morning_raw) > 0:
    if morning_profit <= 1000:
        telegram_bot_sendtext('Odin lost. ' + str(round(morning_profit, 2)))
else:
    open_positions = MT.Get_all_open_positions()
    telegram_bot_sendtext('Total '+str(len(open_positions)) + ' still open. $' + str(round((open_positions['profit'].sum()), 2)))