#SkyCE FX 3.0 Watchlist maker

from datetime import datetime
import pandas as pd
import time
from pathlib import Path
import finnhub
import yfinance as yf
import requests
from bokeh.io import output_file, show, save
from bokeh.layouts import widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, StringFormatter, TableColumn
from bokeh.models import Title
import numpy as np
from get_senti import *
from check_news import *
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
port = 1122 #FXCM MAIN 50k 1:100
list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair
con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup=symbols)

api_key = 'c1iobuf48v6vit2166cg'
finnhub_client = finnhub.Client(api_key=api_key)

if datetime.now().weekday() > 4: #don't run on weekends
    exit()
elif datetime.now().weekday() == 0 and datetime.now().hour < 5:
    exit()
else:
    pass

home = str(Path.home())

t_gram_creds = open((home+'/Desktop/t_gram.txt'), 'r')
bot_token = t_gram_creds.readline().split('\n')[0]
bot_chatID = t_gram_creds.readline()
t_gram_creds.close()


def telegram_bot_sendtext(bot_message):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

def telegram_bot_sendfile(filename, location):
    url = "https://api.telegram.org/bot" + bot_token + "/sendDocument"
    files = {'document': open((location+filename), 'rb')}
    data = {'chat_id' : bot_chatID}
    r= requests.post(url, files=files, data=data)
    print(r.status_code, r.reason, r.content)

def pair_name(currency):
    symbol_dict = {'g':'GBP', 'j':'JPY', 'u':'USD','c':'CAD', 
    'f':'CHF','e':'EUR', 'a':'AUD', 'x':'XAU', 'n':'NZD'}
    first = symbol_dict[list(currency)[0]]
    second = symbol_dict[list(currency)[1]]
    fx_currency = first + second
    return fx_currency

def slice_pair(pair):
    sliced = []
    sliced.append(pair[:3])
    sliced.append(pair[3:6])
    return sliced

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
    levels.append(current_price)
    levels.sort()
    try:
        lower = levels[levels.index(current_price)-1]
        return lower
    except:
        return current_price

def upper_level(current_price, levels):
    levels.append(current_price)
    levels.sort()
    try:
        upper = levels[levels.index(current_price)+2]
        return upper
    except:
        return current_price


def trade(dirxn, symbol, volume=0.01, sl=0, tp=0, comment=''):
    con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup={symbol:symbol})
    new_order = MT.Open_order(instrument=symbol, ordertype=dirxn, volume=volume, openprice = 0.0, slippage = 10, magicnumber=41, stoploss=0.0, takeprofit=0.0, comment = comment)
    if new_order > 0:
        return "Order opened for " + symbol + " (" + dirxn.capitalize() + ")."
    else:
        return "Order opening for " + symbol + " failed."

def sl(dirxn, distance, away_lower, current_price):
    if dirxn == 'SELL':
        sl = current_price + (distance*((1-away_lower)+.06))
        return sl
    elif dirxn == 'BUY':
        sl = current_price - (distance*(away_lower+.06))
        return sl
    else:
        return 0

def vol(away):
    if 0.2 <= away <= 0.25:
        return 2
    elif 0.25 >= away <= 0.30:
        return 1.5
    else:
        return 1

now = datetime.now().strftime("%H:%M %m/%d/%Y")
fx_pairs = []
fx_raw =  ['ac', 'af', 'aj', 'an', 'au', 'cf', 'cj', 'ea', 'ec', 'ef', 'eg', 'ej', 'eu', 'fj', 'ga', 'gf', 'gj', 'gu', 'nc', 'nj', 'nu', 'uc', 'uf', 'uj']
for pair in fx_raw:
    fx_pairs.append(pair_name(pair))

df_pairs = pd.DataFrame()
df_pairs['Currency'] = fx_pairs

fx_score = []
for currency in df_pairs['Currency']:
    score = sentiment_score(currency)
    print(score, currency)
    fx_score.append(score)
    time.sleep(1)
df_pairs['FX Score'] = fx_score

levels = []
for currency in df_pairs['Currency']:
    sr = get_sr(currency, 240)
    levels.append(sr)
    print('SR done: ' + currency)
    time.sleep(2)

df_pairs['Levels'] = levels
# df_pairs['Current Price'] = [yf.Ticker(pair + "=X").info['bid'] for pair in df_pairs['Currency']]

current_price = []
for currency in df_pairs['Currency']:
    raw = MT.Get_last_tick_info(instrument=currency)['bid']
    print(raw,currency)
    current_price.append(raw)

df_pairs['Current Price'] = current_price

lower_levels = []
upper_levels = []

for pair in df_pairs['Currency']:
    current_price = df_pairs['Current Price'][df_pairs['Currency'] == pair].values[0]
    l_levels_raw = []
    l_levels_raw = df_pairs['Levels'][df_pairs['Currency'] == pair]
    l_levels = l_levels_raw.values[0]
    lower_levels.append(lower_level(current_price, l_levels))

for pair in df_pairs['Currency']:
    current_price = df_pairs['Current Price'][df_pairs['Currency'] == pair].values[0]
    u_levels_raw = []
    u_levels_raw = df_pairs['Levels'][df_pairs['Currency'] == pair]
    u_levels = u_levels_raw.values[0]
    upper_levels.append(upper_level(current_price, u_levels))

df_pairs['Upper Level'] = upper_levels
df_pairs['Lower Level'] = lower_levels

df_pairs['Total Distance UL'] = np.array(df_pairs['Upper Level']) - np.array(df_pairs['Lower Level'])
df_pairs['% Away Lower'] = (np.array(df_pairs['Current Price']) - np.array(df_pairs['Lower Level']))/np.array(df_pairs['Total Distance UL'])
df_pairs['% Away Upper'] = (np.array(df_pairs['Upper Level']) - np.array(df_pairs['Current Price']))/np.array(df_pairs['Total Distance UL'])

sr_filter = []

for pair in df_pairs['Currency']:
    if (df_pairs['FX Score'][df_pairs['Currency'] == pair].values[0] < 0) and (0.2 <= df_pairs['% Away Upper'][df_pairs['Currency'] == pair].values[0] <= 0.30):
        sr_filter.append('SELL')
    elif (df_pairs['FX Score'][df_pairs['Currency'] == pair].values[0] < 0) and (0.31 <= df_pairs['% Away Upper'][df_pairs['Currency'] == pair].values[0] <= 0.40):
        sr_filter.append('SELL WATCHLIST')
    elif (df_pairs['FX Score'][df_pairs['Currency'] == pair].values[0] > 0) and (0.2 <= df_pairs['% Away Lower'][df_pairs['Currency'] == pair].values[0] <= 0.30):
        sr_filter.append('BUY')
    elif (df_pairs['FX Score'][df_pairs['Currency'] == pair].values[0] > 0) and (0.31 <= df_pairs['% Away Lower'][df_pairs['Currency'] == pair].values[0] <= 0.40):
        sr_filter.append('BUY WATCHLIST')
    else:
        sr_filter.append('NEUTRAL')

df_pairs['SR Filter'] = sr_filter
df_pairs.to_csv(home + '/Desktop/Experimental/v3/raw_watchlist.csv', index=False)
df_watchlist = df_pairs[df_pairs['SR Filter'] != 'NEUTRAL']
columns = ['Currency', 'FX Score','Lower Level', 'Upper Level', 'SR Filter']
df_watchlist_final = df_watchlist[columns][df_watchlist['SR Filter'].str.contains('WATCHLIST')]
df_watchlist_old = pd.read_csv(home + '/Desktop/Experimental/v3/fx_watchlist.csv')
df_watchlist_old = df_watchlist_old.append(df_watchlist_final)
df_watchlist_old.drop_duplicates(subset=['Currency'], keep='last', inplace=True)
df_watchlist_old.to_csv(home + '/Desktop/Experimental/v3/fx_watchlist.csv', index = False)
filename = 'fx_watchlist.csv'
location = home + '/Desktop/Experimental/v3/'
telegram_bot_sendfile(filename=filename, location=location)
telegram_bot_sendtext('Saved watchlist.')   

ready_to_trade = df_pairs[['Currency', 'FX Score', 'SR Filter','Total Distance UL', 'Current Price', '% Away Lower', '% Away Upper']][(df_pairs['SR Filter'] == 'BUY') | (df_pairs['SR Filter'] == 'SELL')]
positions = MT.Get_all_open_positions()
all_pairs = set(list(positions['instrument']))

for currency in ready_to_trade['Currency']:
    if currency in all_pairs:
        curr_index = ready_to_trade[ready_to_trade['Currency'] == currency].index.values[0]
        ready_to_trade.drop([curr_index], inplace=True)
        telegram_bot_sendtext(currency + ' ready to trade from screener but has exceeded open positions allowed.')

# sl = []
# vol = []

# for currency in ready_to_trade['Currency']:
#     dirxn = ready_to_trade['SR Filter'][ready_to_trade['Currency'] == currency].values[0]
#     distance = ready_to_trade['Total Distance UL'][ready_to_trade['Currency'] == currency].values[0]
#     current_price = ready_to_trade['Current Price'][ready_to_trade['Currency'] == currency].values[0]
#     away_lower = ready_to_trade['% Away Lower'][ready_to_trade['Currency'] == currency].values[0]
#     away_upper = ready_to_trade['% Away Upper'][ready_to_trade['Currency'] == currency].values[0]
#     x = sl(dirxn=dirxn,distance = distance, away_lower = away_lower, current_price = current_price) 
#     sl.append(x)
#     if dirxn == 'SELL':
#         vol.append(vol(away_upper))
#     elif dirxn == 'BUY':
#         vol.append(vol(away_upper))

# ready_to_trade['SL'] = sl
# ready_to_trade['Volume'] = vol
vol = 2
if len(ready_to_trade) > 0:
    telegram_bot_sendfile(filename='signals_scanner.html', location= home + '/Desktop/Experimental/v3/')
    for currency in ready_to_trade['Currency']:
        # sl = ready_to_trade['SL'][ready_to_trade['Currency'] == currency].values[0]
        # vol = ready_to_trade['Volume'][ready_to_trade['Currency'] == currency].values[0]
        if (ready_to_trade['SR Filter'][ready_to_trade['Currency'] == currency].values[0] == 'BUY') and (ready_to_trade['FX Score'][ready_to_trade['Currency'] == currency].values[0] > 3):
            dirxn = 'buy'
            msg = now + '\n' + currency + ' is ready to trade from screener. (' + dirxn + ')\n'
            telegram_bot_sendtext(msg)
            # validation, events = check_news(currency)
            # if validation == True:
            #     telegram_bot_sendtext(currency, ' got news.', str(events))
            # else:
            #     pass
            try:
                trade(dirxn=dirxn,symbol=currency,volume=vol, sl=0, tp=0)
                telegram_bot_sendtext('Position opened successfully: ' + currency + ' (' + dirxn.upper() + ')')
            except:
                telegram_bot_sendtext('Error opening position: ' + currency + ' (' + dirxn.upper() + ')')
        elif (ready_to_trade['SR Filter'][ready_to_trade['Currency'] == currency].values[0] == 'SELL') and (ready_to_trade['FX Score'][ready_to_trade['Currency'] == currency].values[0] < -3):
            dirxn = 'sell'
            msg = now + '\n' + currency + ' is ready to trade from screener. (' + dirxn + ')\n'
            telegram_bot_sendtext(msg)
            # validation, events = check_news(currency)
            # if validation == True:
            #     telegram_bot_sendtext(currency, ' got news.', str(events))
            # else:
            #     pass
            try:
                trade(dirxn=dirxn,symbol=currency,volume=vol, sl=0, tp=0)
                telegram_bot_sendtext('Position opened successfully: ' + currency + ' (' + dirxn.upper() + ')')
            except:
                telegram_bot_sendtext('Error opening position: ' + currency + ' (' + dirxn.upper() + ')')
else:
    telegram_bot_sendtext('No trades from screener.')

print('Done.')