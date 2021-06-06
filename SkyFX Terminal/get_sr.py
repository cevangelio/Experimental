##get SR

import pandas as pd
import time
from pathlib import Path
import finnhub
import yfinance as yf
import requests
import numpy as np
import datetime
from datetime import datetime, timedelta
import sys
home = str(Path.home())


home = str(Path.home())
api_key = 'c1iobuf48v6vit2166cg'
finnhub_client = finnhub.Client(api_key=api_key)

def get_current_price(symbol):
    price = yf.Ticker(symbol + "=X").info['bid']
    return price

def symbol_maker(pair):
    if len(pair) != 6:
        return "Error. Not a valid pair."
    else:
        final = "OANDA:" + pair[:3].upper() + "_" + pair[3:6].upper()
        return final

def get_sr(symbol,tf=240):
    '''
    tf = 1, 5, 15, 30, 60, 240, D, W, M

    '''
    symbol = symbol_maker(symbol)
    try:
        raw = requests.get('https://finnhub.io/api/v1/scan/support-resistance?symbol='+symbol+'&resolution='+str(tf)+'&token='+api_key)
        levels = raw.json()['levels']
        return levels
    except:
        print("Error: Check arguments.")

def lower_level(current_price, levels):
    n = len(levels)
    levels.append(current_price)
    levels = list(set(levels))
    levels.sort()
    if levels.index(current_price) == 0:
        return current_price
    else:
        lower = levels[levels.index(current_price)-1]
        return lower

def upper_level(current_price, levels):
    levels.append(current_price)
    levels = list(set(levels))
    levels.sort(reverse=True) #ascending
    if levels.index(current_price) == 0:
        return current_price
    else:
        upper = levels[levels.index(current_price)-1]
        return upper