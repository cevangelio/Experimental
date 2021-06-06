import pandas as pd
import time
from pathlib import Path
import finnhub
import yfinance as yf
import requests
import numpy as np
import datetime
from datetime import datetime, timedelta
home = str(Path.home())


home = str(Path.home())
api_key = 'c1iobuf48v6vit2166cg'
finnhub_client = finnhub.Client(api_key=api_key)

def symbol_maker(pair):
    if len(pair) != 6:
        return "Error. Not a valid pair."
    else:
        final = "OANDA:" + pair[:3].upper() + "_" + pair[3:6].upper()
        return final

def get_sr(symbol,tf=240):
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

df = pd.read_csv(home + '\Desktop\senti.csv')
df_pairs_filtered = df
df_pairs_filtered['FX Score converted'] = np.absolute(df['FX Score'])
df_pairs_filtered.sort_values(by = ['FX Score converted'], inplace=True, ascending=False)
df_pairs_filtered.reset_index(inplace=True)
df_pairs_filtered.drop(columns = ['index'], inplace=True)
# df_pairs_filtered = df[df['FX Score converted'] > 5]
levels = []
for currency in df_pairs_filtered['Currency']:
    sr = get_sr(currency, 240)
    levels.append(sr)
    time.sleep(1)
df_pairs_filtered['Levels'] = levels
df_pairs_filtered['Current Price'] = [yf.Ticker(pair + "=X").info['bid'] for pair in df_pairs_filtered['Currency']]
lower_levels = []
upper_levels = []

for pair in df_pairs_filtered['Currency']:
    current_price = df_pairs_filtered['Current Price'][df_pairs_filtered['Currency'] == pair].values[0]
    l_levels_raw = []
    l_levels_raw = df_pairs_filtered['Levels'][df_pairs_filtered['Currency'] == pair]
    l_levels = l_levels_raw.values[0]
    lower_levels.append(lower_level(current_price, l_levels))

for pair in df_pairs_filtered['Currency']:
    current_price = df_pairs_filtered['Current Price'][df_pairs_filtered['Currency'] == pair].values[0]
    u_levels_raw = []
    u_levels_raw = df_pairs_filtered['Levels'][df_pairs_filtered['Currency'] == pair]
    u_levels = u_levels_raw.values[0]
    upper_levels.append(upper_level(current_price, u_levels))

df_pairs_filtered['Lower Level'] = lower_levels
df_pairs_filtered['Upper Level'] = upper_levels

print(df_pairs_filtered)

#percent away from level

df_pairs_filtered['Total Distance UL'] = np.array(df_pairs_filtered['Upper Level']) - np.array(df_pairs_filtered['Lower Level'])
df_pairs_filtered['% Away Lower'] = (np.array(df_pairs_filtered['Current Price']) - np.array(df_pairs_filtered['Lower Level']))/np.array(df_pairs_filtered['Total Distance UL'])
df_pairs_filtered['% Away Upper'] = (np.array(df_pairs_filtered['Upper Level']) - np.array(df_pairs_filtered['Current Price']))/np.array(df_pairs_filtered['Total Distance UL'])

# SR FILTER
sr_filter = [] #30% away from SL + 70% from TP

for pair in df_pairs_filtered['Currency']:
    if (df_pairs_filtered['FX Score'][df_pairs_filtered['Currency'] == pair].values[0] < 0) and (0 <= df_pairs_filtered['% Away Upper'][df_pairs_filtered['Currency'] == pair].values[0] <= 0.20):
        sr_filter.append('SELL LIMIT')
    elif (df_pairs_filtered['FX Score'][df_pairs_filtered['Currency'] == pair].values[0] < 0) and (0.21 <= df_pairs_filtered['% Away Upper'][df_pairs_filtered['Currency'] == pair].values[0] <= 0.4):
        sr_filter.append('SELL')
    elif (df_pairs_filtered['FX Score'][df_pairs_filtered['Currency'] == pair].values[0] < 0) and (0.80 <= df_pairs_filtered['% Away Upper'][df_pairs_filtered['Currency'] == pair].values[0] <= 1):
        sr_filter.append('SELL WATCHLIST')
    elif (df_pairs_filtered['FX Score'][df_pairs_filtered['Currency'] == pair].values[0] > 0) and (0 <= df_pairs_filtered['% Away Lower'][df_pairs_filtered['Currency'] == pair].values[0] <= 0.20):
        sr_filter.append('BUY LIMIT')
    elif (df_pairs_filtered['FX Score'][df_pairs_filtered['Currency'] == pair].values[0] > 0) and (0.21 <= df_pairs_filtered['% Away Lower'][df_pairs_filtered['Currency'] == pair].values[0] <= 0.40):
        sr_filter.append('BUY')
    elif (df_pairs_filtered['FX Score'][df_pairs_filtered['Currency'] == pair].values[0] > 0) and (0.80 <= df_pairs_filtered['% Away Lower'][df_pairs_filtered['Currency'] == pair].values[0] <= 1):
        sr_filter.append('BUY WATCHLIST')
    else:
        sr_filter.append('NEUTRAL')

df_pairs_filtered['SR Filter'] = sr_filter
print(df_pairs_filtered[(df_pairs_filtered['SR Filter'] != 'NEUTRAL') & (df_pairs_filtered['FX Score converted'] > 3)]) #removed everything not needed

##add to watchlist

df_watchlist = df_pairs_filtered[(df_pairs_filtered['SR Filter'] != 'NEUTRAL') & (df_pairs_filtered['FX Score converted'] > 3)]
columns = ['Currency', 'FX Score', 'Lower Level', 'Upper Level', 'SR Filter']
df_watchlist_final = df_watchlist[columns][df_watchlist['SR Filter'].str.contains('WATCHLIST')]
df_watchlist_final.to_csv('fx_watchlist.csv', index=False)
df_pairs_filtered.to_csv('test2.csv',index=False)