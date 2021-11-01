'''
entry: 3bars+3bars
200ema
SL: 2atr
TP: 4atr (at least)
'''

import numpy as np
import pandas as pd
import requests
import datetime
from datetime import date, datetime
import time
from pathlib import Path
import pandas_ta as ta
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
ports = [1127]
port_dict = {1122:'FTMO', 1125:'FXCM', 1127:'GP'}

list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCAD','GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'NZDCHF','USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair
con = ""
try:
    con = MT.Connect(server='192.168.1.2', port=1127, instrument_lookup=symbols)
except:
    con = MT.Connect(server='127.0.0.1', port=1127, instrument_lookup=symbols)

def bar_color(bar):
    if bar['open'] > bar['close']:
        return 'red'
    elif bar['open'] < bar['close']:
        return 'green'
    else:
        return 'ignore'


home = str(Path.home())
t_gram_creds = open((home+'/Desktop/t_gram.txt'), 'r')
bot_token = t_gram_creds.readline().split('\n')[0]
bot_chatID = t_gram_creds.readline()
t_gram_creds.close()

def telegram_bot_sendtext(bot_message):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

tf = 'H1'

df_raw = pd.DataFrame()
df_raw['Currency'] = list_symbols
atr_l = []

action = []
for currency in list_symbols:
    bars = pd.DataFrame(MT.Get_last_x_bars_from_now(instrument = currency, timeframe = MT.get_timeframe_value(tf), nbrofbars=1800))
    print(currency)
    bars['200ema'] = ta.sma(bars['close'], length = 200)
    atr_raw = ta.atr(high = bars['high'], low = bars['low'], close = bars['close'],mamode = 'EMA')
    bars['atr'] = atr_raw
    atr = atr_raw[len(bars) - 2] #last value
    atr_l.append(atr)
    bar1 = bars.loc[len(bars) -7]
    bar2 = bars.loc[len(bars) -6]
    bar3 = bars.loc[len(bars) -5]
    bar4 = bars.loc[len(bars) -4]
    bar5 = bars.loc[len(bars) -3]
    bar6 = bars.loc[len(bars) -2]
    bar1_color = bar_color(bar1)
    bar2_color = bar_color(bar2)
    bar3_color = bar_color(bar3)
    bar4_color = bar_color(bar4)
    bar5_color = bar_color(bar5)
    bar6_color = bar_color(bar6)
    if bar1_color == 'green' and bar2_color == 'green' and bar3_color == 'green' and bar4_color == 'red' and bar5_color == 'red' and bar6_color == 'red' and (bars['close'].loc[len(bars)-2] > bars['200ema'].loc[len(bars)-2]):
        action.append('buy')
    elif bar1_color == 'red' and bar2_color == 'red' and bar3_color == 'red' and bar4_color == 'green' and bar5_color == 'green' and bar6_color == 'green' and (bars['close'].loc[len(bars)-2] < bars['200ema'].loc[len(bars)-2]):
        action.append('sell')
    elif bar1_color == 'green' and bar2_color == 'green' and bar3_color == 'green' and bar4_color == 'red' and bar5_color == 'red' and bar6_color == 'red' and (bars['close'].loc[len(bars)-2] < bars['200ema'].loc[len(bars)-2]):
        action.append('sell')
    elif bar1_color == 'red' and bar2_color == 'red' and bar3_color == 'red' and bar4_color == 'green' and bar5_color == 'green' and bar6_color == 'green' and (bars['close'].loc[len(bars)-2] > bars['200ema'].loc[len(bars)-2]):
        action.append('buy')
    # elif bar1_color == 'green' and bar2_color == 'green' and bar3_color == 'red' and bar4_color == 'red' and bar5_color == 'red' and bar6_color == 'green' and (bars['close'].loc[len(bars)-2] < bars['ema'].loc[len(bars)-2]):
    #     action.append('sell_s')
    # elif bar1_color == 'red' and bar2_color == 'red' and bar3_color == 'green' and bar4_color == 'green' and bar5_color == 'green' and bar6_color == 'red' and (bars['close'].loc[len(bars)-2] > bars['ema'].loc[len(bars)-2]):
    #     action.append('buy_s')
    else:
        action.append('ignore')

df_raw['Action'] = action
df_raw['atr'] = atr_l

sl = []
tp = []
for line in range(0, len(df_raw)):
    if df_raw['Action'].loc[line] == 'buy':
        sl.append((df_raw['Current Price'].loc[line]) - (3*(df_raw['atr'].loc[line])))
        tp.append((df_raw['Current Price'].loc[line]) + (5*(df_raw['atr'].loc[line])))
    elif df_raw['Action'].loc[line] == 'sell':
        sl.append((df_raw['Current Price'].loc[line]) + (3*(df_raw['atr'].loc[line])))
        tp.append((df_raw['Current Price'].loc[line]) - (5*(df_raw['atr'].loc[line])))
    else:
        sl.append(0)
        tp.append(0)
df_raw['sl'] = sl
df_raw['tp'] = tp

print(df_raw)
to_trade = df_raw[df_raw['Action'] != 'ignore']
if len(to_trade) == 0:
    telegram_bot_sendtext('No trad3s. ')
else:
    telegram_bot_sendtext(str(len(to_trade))+ ' setup found. ' +str(set(to_trade['Currency'])))

for pair in to_trade['Currency']:
    dirxn = to_trade['Action'][to_trade['Currency'] == pair].values[0]
    sloss = to_trade['Action'][to_trade['sl'] == pair].values[0]
    tprof = to_trade['Action'][to_trade['tp'] == pair].values[0]
    vol = 0.03
    order = MT.Open_order(instrument=pair, ordertype=dirxn, volume=vol, openprice = 0.0, slippage = 10, magicnumber=33, stoploss=sloss, takeprofit=tprof, comment ='trad3')
    if order != -1:    
        telegram_bot_sendtext('Trad3 setup found. Position opened successfully: ' + pair + ' (' + dirxn.upper() + ')')
        time.sleep(3)
    else:
        telegram_bot_sendtext('Trade3 setup found. ' + (MT.order_return_message).upper() + ' For ' + pair + ' (' + dirxn.upper() + ')')




    