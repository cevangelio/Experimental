import pandas as pd
import requests
import datetime
from datetime import date, datetime
import time
from pathlib import Path
import pandas_ta as ta
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
port = [1122, 1125, 1127] #FXCM MAIN 50k 1:100
port_dict = {1122:'FTMO', 1125:'FXCM', 1127:'Global_Prime'}
list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair
def mt4connect(port):
    con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup=symbols)
    return con