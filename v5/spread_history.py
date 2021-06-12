#spread history maker

import numpy as np
import pandas as pd
import requests
import datetime
from datetime import datetime
import os
import time
from pathlib import Path
import pandas_ta as ta
from get_signal import *
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
port = 1122 #FXCM MAIN 50k 1:100
list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCAD','GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair
con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup=symbols)

home = str(Path.home())

df_raw = pd.DataFrame()
df_raw['Currency'] = list_symbols
spread_l = []

for currency in df_raw['Currency']:
    bars = pd.DataFrame(MT.Get_last_x_ticks_from_now(instrument=currency, nbrofticks=800))
    bars['spread raw'] = np.array(bars['bid']) - np.array(bars['ask'])
    spread_raw = bars['spread raw'].mean()
    point = MT.Get_instrument_info(instrument=currency)['point']
    spread = round(abs(spread_raw/point), 0)
    print(currency, ' - ', spread)
    spread_l.append(spread)

df_raw['avg spread'] = spread_l
df_raw.to_csv(home+'/Desktop/Experimental/v5/spread.csv')