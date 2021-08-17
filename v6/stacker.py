#stacker

import pandas as pd
import requests
import datetime
from datetime import date, datetime
import time
from pathlib import Path
import pandas_ta as ta
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
ports = [1122, 1125, 1127]
port_dict = {1122:'FTMO', 1125:'FXCM', 1127:'GP'}

list_symbols = ['AUDCAD','AUDUSD','EURUSD', 'GBPUSD','NZDUSD','USDCAD','USDCHF','USDJPY'] #2021 best performing
# list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCAD','GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair
con = MT.Connect(server='127.0.0.1', port=1125, instrument_lookup=symbols)

currency_data = pd.read_csv('d:/TradeJournal/cerberus_raw.csv')

for pair in list_symbols:
    atr = currency_data['atr'][currency_data['Currency'] == pair].values[0]
    open_price = 0
    current_price = 0
    # get amount of move (open - current), divide move by ATR, if more than 1.5, add limit price to 1.5
