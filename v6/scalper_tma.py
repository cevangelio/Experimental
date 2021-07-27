'''
source: best scalping strategy period by moving average

rsi - len:14, 50 (same tf)
smoothed MA (30,50,200)- must be sloping, price above all 3
williams fractal - tapy or when price is nearest 30, around 5-10% distance(?)
tf = 5 min
exit = 10 pips?
stop = below low of prev candle

'''

import pandas as pd
import requests
import datetime
from datetime import date, datetime
import time
from pathlib import Path
import pandas_ta as ta
from tapy import Indicators
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
port = 1122 #FXCM MAIN 50k 1:100
list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCAD','GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair
con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup=symbols)

home = str(Path.home())
t_gram_creds = open((home+'/Desktop/t_gram.txt'), 'r')
bot_token = t_gram_creds.readline().split('\n')[0]
bot_chatID = t_gram_creds.readline()
t_gram_creds.close()

def telegram_bot_sendtext(bot_message):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

currency = 'EURUSD'
tf = 'M5'
bars = pd.DataFrame(MT.Get_last_x_bars_from_now(instrument = currency, timeframe = MT.get_timeframe_value(tf), nbrofbars=600))
current_price = bars['close'].loc[len(bars) - 1]
i = Indicators(bars)
i.smma(period=30, column_name = 'smma30', apply_to = 'close')
i.smma(period=50, column_name = 'smma50', apply_to = 'close')
i.smma(period=200, column_name = 'smma200', apply_to = 'close')
rsi_raw = ta.rsi(bars['close'], length = 14)
df = i.df
df['rsi'] = rsi_raw