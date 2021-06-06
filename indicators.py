import finnhub
import requests
from datetime import datetime, timedelta
from pathlib import Path
import time
import yfinance as yf
import pandas as pd

home = str(Path.home())
api_key = 'c1iobuf48v6vit2166cg'
finnhub_client = finnhub.Client(api_key=api_key)

def pair_name(currency):
    symbol_dict = {'g':'GBP', 'j':'JPY', 'u':'USD','c':'CAD', 
    'f':'CHF','e':'EUR', 'a':'AUD', 'x':'XAU', 'n':'NZD'}
    first = symbol_dict[list(currency)[0]]
    second = symbol_dict[list(currency)[1]]
    fx_currency = first + second
    return fx_currency

def symbol_maker(pair):
    if len(pair) != 6:
        return "Error. Not a valid pair."
    else:
        final = "OANDA:" + pair[:3].upper() + "_" + pair[3:6].upper()
        return final

def get_sr(symbol,tf=60):
    '''
    tf = 1, 5, 15, 30, 60, D, W, M

    '''
    symbol = symbol_maker(symbol)
    try:
        raw = requests.get('https://finnhub.io/api/v1/scan/support-resistance?symbol='+symbol+'&resolution='+str(tf)+'&token='+api_key)
        levels = raw.json()['levels']
        return levels
    except:
        print("Error: Check arguments.")

def get_atr(symbol, tf=60, length=20):
    now = datetime.now()
    start_timestamp = str(int(datetime.timestamp(now)))
    end_timestamp = str(int(datetime.timestamp(now-timedelta(40))))
    symbol = symbol_maker(symbol)
    atr_raw = requests.get('https://finnhub.io/api/v1/indicator?symbol='+symbol+'&resolution='+str(tf)+'&from='+start_timestamp+'&to'+end_timestamp+'&indicator=atr&timeperiod='+str(length)+'&token='+api_key)
    return atr_raw

def lower_level(x, l):
    l.append(x)
    l.sort()
    lower = l[l.index(x)-1]
    return lower

def upper_level(x, l):
    l.append(x)
    l.sort()
    upper = l[l.index(x)+2]
    return upper


#how to get support and resistance

df = pd.read_csv(home + '\Desktop\senti.csv')

levels = []
for currency in df['Currency']:
    sr = get_sr(currency, 240)
    levels.append(sr)
    time.sleep(1)

df['Levels'] = levels

#get_current price

df['Current Price'] = [yf.Ticker(pair + "=X").info['bid'] for pair in df['Currency']]

#get in between SR level

lower_levels = []
upper_levels = []
for pair in df['Currency']:
    current_price = df['Current Price'][df['Currency'] == pair].values[0]
    levels_raw = []
    levels_raw = df['Levels'][df['Currency'] == pair]
    levels = levels_raw.values[0]
    lower_levels.append(lower_level(current_price, levels))
    upper_levels.append(upper_level(current_price, levels))

df['Upper Level'] = upper_levels
df['Lower Level'] = lower_levels

df.to_csv('level_test_2.csv', index=False)

print(df)

'''

