'''
entry: 3bars+3bars
200ema
SL: 2atr
TP: 4atr (at least)
'''

from numpy import append
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
    con = MT.Connect(server='192.168.1.2', port=1125, instrument_lookup=symbols)
except:
    con = MT.Connect(server='127.0.0.1', port=1125, instrument_lookup=symbols)

def bar_color(bar):
    if bar['open'] > bar['close']:
        return 'red'
    elif bar['open'] < bar['close']:
        return 'green'
    else:
        return 'ignore'

tf = 'H4'

df_raw = pd.DataFrame()
df_raw['Currency'] = list_symbols

action = []
for currency in list_symbols:
    bars = pd.DataFrame(MT.Get_last_x_bars_from_now(instrument = currency, timeframe = MT.get_timeframe_value(tf), nbrofbars=1800))
    print(currency)
    bars['200ema'] = ta.sma(bars['close'], length = 200)
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
        action.append('sell_r')
    elif bar1_color == 'red' and bar2_color == 'red' and bar3_color == 'red' and bar4_color == 'green' and bar5_color == 'green' and bar6_color == 'green' and (bars['close'].loc[len(bars)-2] > bars['200ema'].loc[len(bars)-2]):
        action.append('buy_r')
    # elif bar1_color == 'green' and bar2_color == 'green' and bar3_color == 'red' and bar4_color == 'red' and bar5_color == 'red' and bar6_color == 'green' and (bars['close'].loc[len(bars)-2] < bars['ema'].loc[len(bars)-2]):
    #     action.append('sell_s')
    # elif bar1_color == 'red' and bar2_color == 'red' and bar3_color == 'green' and bar4_color == 'green' and bar5_color == 'green' and bar6_color == 'red' and (bars['close'].loc[len(bars)-2] > bars['ema'].loc[len(bars)-2]):
    #     action.append('buy_s')
    else:
        action.append('ignore')

df_raw['Action'] = action

print(df_raw)

    