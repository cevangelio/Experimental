#get data for backtest

from datetime import timedelta
import numpy as np
import pandas as pd
from pathlib import Path
import time
import os
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
port = 1122 #FXCM MAIN 50k 1:100
list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCAD','GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair
con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup=symbols)

home = str(Path.home())
for currency in list_symbols:
    x_bars = 1000
    tf = 'D1'
    bars = pd.DataFrame(MT.Get_last_x_bars_from_now(instrument = currency, timeframe = MT.get_timeframe_value(tf), nbrofbars=x_bars))

    date = []
    # time_l = []

    # for x in range(0, 1000):
    #     raw = (datetime.now() - timedelta(1000)) + timedelta(x)
    #     date.append(datetime.strftime(raw, '%Y-%m-%d %H:%M:%S'))

    for x in bars['date']:
        date_conv = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(x))
        # time_conv = time.strftime('', time.localtime(x))
        date.append(date_conv)
        # time_l.append(time_conv)

    bars.drop(columns=['date'],inplace=True)
    bars['date'] = date
    # bars['time'] = time_l
    # bars[['date', 'time', 'open', 'high', 'low', 'close', 'volume']].to_csv(currency+'.csv', index=False)
    bars[['date', 'open', 'high', 'low', 'close', 'volume']].to_csv(home + '/Desktop/Experimental/v5/backtest_files/'+currency+'.csv', index=False)