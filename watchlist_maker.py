#Get Tradingview Analysis

from tradingview_ta import TA_Handler, Interval
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
import pymt5adapter as mta
from pymt5adapter.order import Order
from pymt5adapter.symbol import Symbol
import MetaTrader5 as mt5
import pandas_ta as ta
import numpy as np
import os

api_key = 'c1iobuf48v6vit2166cg'
finnhub_client = finnhub.Client(api_key=api_key)

# avoid = [0,1,5,6] #not trading on Monday, Tuesday, Saturday, Sunday
if datetime.now().weekday() > 4:
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

def telegram_bot_sendphoto():
    url = "https://api.telegram.org/bot" + bot_token + "/sendPhoto"
    files = {'photo': open('signals.png', 'rb')}
    data = {'chat_id' : bot_chatID}
    r= requests.post(url, files=files, data=data)
    print(r.status_code, r.reason, r.content)

def telegram_bot_sendfile(filename):
    url = "https://api.telegram.org/bot" + bot_token + "/sendDocument"
    files = {'document': open((home +'\Desktop' + '\/' + filename), 'rb')}
    data = {'chat_id' : bot_chatID}
    r= requests.post(url, files=files, data=data)
    print(r.status_code, r.reason, r.content)

def get_senti(fx_currency, period):
    # print(fx_currency)
    handler = TA_Handler()
    handler.set_symbol_as(fx_currency)
    handler.set_exchange_as_forex()
    handler.set_screener_as_forex()
    if period == '15m':
        handler.set_interval_as(Interval.INTERVAL_15_MINUTES)
        analysis = handler.get_analysis().summary
        return analysis
    elif period == '4h':
        handler.set_interval_as(Interval.INTERVAL_4_HOURS)
        analysis = handler.get_analysis().summary
        return analysis
    elif period == '1h':
        handler.set_interval_as(Interval.INTERVAL_1_HOUR)
        analysis = handler.get_analysis().summary
        return analysis
    elif period == '1d':
        handler.set_interval_as(Interval.INTERVAL_1_DAY)
        analysis = handler.get_analysis().summary
        return analysis
    
def pair_name(currency):
    symbol_dict = {'g':'GBP', 'j':'JPY', 'u':'USD','c':'CAD', 
    'f':'CHF','e':'EUR', 'a':'AUD', 'x':'XAU', 'n':'NZD'}
    first = symbol_dict[list(currency)[0]]
    second = symbol_dict[list(currency)[1]]
    fx_currency = first + second
    return fx_currency

def sentiment_score(data):#reversed
    buy = list(data).count('BUY')
    sbuy = list(data).count('STRONG_BUY')
    sell = list(data).count('SELL')
    ssell = list(data).count('STRONG_SELL')
    total_score = buy + 3*sbuy + (-1*sell) + (-3*ssell)
    return total_score

def trade(dirxn, symbol, volume, sl=0, tp=0):
    if dirxn == 'buy':
        order = Order.as_buy(symbol=symbol, volume=volume)
        order.send()
    elif dirxn == 'sell':
        order = Order.as_sell(symbol=symbol, volume=volume)
        order.send()
    print(dirxn + ' order placed for ' + symbol + ' at ' + str(volume) + ' lot size.')

def slice_pair(pair):
    sliced = []
    sliced.append(pair[:3])
    sliced.append(pair[3:6])
    return sliced

def compare_score(pair1, pair2):
    higher_score_pair = ""
    pair1_score = max(abs(df_pairs['FX Score'][df_pairs['Currency'] == pair1]))
    pair2_score = max(abs(df_pairs['FX Score'][df_pairs['Currency'] == pair2]))
    if pair1_score > pair2_score:
        higher_score_pair = pair1
    if pair2_score > pair1_score:
        higher_score_pair = pair2
    else:
        higher_score_pair = pair1
    return higher_score_pair

def detect_duplicate(pair1,pair2):
    a_set = set(slice_pair(pair1))
    b_set = set(slice_pair(pair2))
    if len(a_set.intersection(b_set)) > 0:
        return True
    return False

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

fx_pairs = []
fx_raw =  ['ac', 'af', 'aj', 'an', 'au', 'cf', 'cj', 'ea', 'ec', 'ef', 'eg', 'ej', 'eu', 'fj', 'ga', 'gf', 'gj', 'gu', 'nc', 'nj', 'nu', 'uc', 'uf', 'uj']
for pair in fx_raw:
    fx_pairs.append(pair_name(pair))

df_pairs = pd.DataFrame(columns=['Currency', '15m', '1h', '4h', '1d'])
df_pairs['Currency'] = fx_pairs

min_15 = []
hour_1 = []
hour_4 = []
day_1 = []

for pair in df_pairs['Currency']:
    min_15.append(get_senti(pair,'15m')['RECOMMENDATION'])
    time.sleep(2)
    hour_1.append(get_senti(pair,'1h')['RECOMMENDATION'])
    time.sleep(2)
    hour_4.append(get_senti(pair,'4h')['RECOMMENDATION'])
    time.sleep(2)
    day_1.append(get_senti(pair, '1d')['RECOMMENDATION'])
    time.sleep(2)
    print("Done for " + pair + '.')

df_pairs['15m'] = min_15
df_pairs['1h'] = hour_1
df_pairs['4h'] = hour_4
df_pairs['1d'] = day_1

score = []
for x in range(0, len(df_pairs)):
    score.append(sentiment_score(df_pairs.loc[x]))

df_pairs['FX Score'] = score

print(df_pairs)
df_pairs.to_csv(home + '\Desktop\senti.csv', index=False)

#filter high value pairs
df_pairs_filtered = df_pairs
df_pairs_filtered['FX Score converted'] = np.absolute(df_pairs['FX Score'])
df_pairs_filtered.sort_values(by = ['FX Score converted'], inplace=True, ascending=False)
df_pairs_filtered.reset_index(inplace=True)
df_pairs_filtered.drop(columns = ['index'], inplace=True)
df_pairs_filtered = df_pairs_filtered[df_pairs_filtered['FX Score converted'] > 3] #get only above 6
above_six_pairs = len(df_pairs_filtered)

##Upper/Lower SR

levels = []
for currency in df_pairs_filtered['Currency']:
    sr = get_sr(currency, 240)
    levels.append(sr)
    print('SR done: ' + currency)
    time.sleep(2)

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

df_pairs_filtered['Upper Level'] = upper_levels
df_pairs_filtered['Lower Level'] = lower_levels

df_pairs_filtered['Total Distance UL'] = np.array(df_pairs_filtered['Upper Level']) - np.array(df_pairs_filtered['Lower Level'])
df_pairs_filtered['% Away Lower'] = (np.array(df_pairs_filtered['Current Price']) - np.array(df_pairs_filtered['Lower Level']))/np.array(df_pairs_filtered['Total Distance UL'])
df_pairs_filtered['% Away Upper'] = (np.array(df_pairs_filtered['Upper Level']) - np.array(df_pairs_filtered['Current Price']))/np.array(df_pairs_filtered['Total Distance UL'])

sr_filter = []
for pair in df_pairs_filtered['Currency']:
    if (df_pairs_filtered['FX Score'][df_pairs_filtered['Currency'] == pair].values[0] < 0) and (0 <= df_pairs_filtered['% Away Upper'][df_pairs_filtered['Currency'] == pair].values[0] <= 0.20):
        sr_filter.append('BUY')
    elif (df_pairs_filtered['FX Score'][df_pairs_filtered['Currency'] == pair].values[0] < 0) and (0.21 <= df_pairs_filtered['% Away Upper'][df_pairs_filtered['Currency'] == pair].values[0] <= 0.4):
        sr_filter.append('BUY WATCHLIST')
    elif (df_pairs_filtered['FX Score'][df_pairs_filtered['Currency'] == pair].values[0] < 0) and (0.80 <= df_pairs_filtered['% Away Upper'][df_pairs_filtered['Currency'] == pair].values[0] <= 1):
        sr_filter.append('BUY WATCHLIST')
    elif (df_pairs_filtered['FX Score'][df_pairs_filtered['Currency'] == pair].values[0] > 0) and (0 <= df_pairs_filtered['% Away Lower'][df_pairs_filtered['Currency'] == pair].values[0] <= 0.20):
        sr_filter.append('SELL')
    elif (df_pairs_filtered['FX Score'][df_pairs_filtered['Currency'] == pair].values[0] > 0) and (0.21 <= df_pairs_filtered['% Away Lower'][df_pairs_filtered['Currency'] == pair].values[0] <= 0.40):
        sr_filter.append('SELL WATCHLIST')
    elif (df_pairs_filtered['FX Score'][df_pairs_filtered['Currency'] == pair].values[0] > 0) and (0.80 <= df_pairs_filtered['% Away Lower'][df_pairs_filtered['Currency'] == pair].values[0] <= 1):
        sr_filter.append('SELL WATCHLIST')
    else:
        sr_filter.append('NEUTRAL')

df_pairs_filtered['SR Filter'] = sr_filter
df_pairs_filtered.to_csv(home+'\Desktop\signals.csv', index=False)

### df to table/img

df_scanner_results = df_pairs_filtered[['Currency', '15m', '1h', '4h', '1d', 'FX Score', 'Upper Level', 'Lower Level', 'Total Distance UL', 'SR Filter']]
df_scanner_results['Upper Level-x'] = np.round(np.array(df_scanner_results['Upper Level']), 5)
df_scanner_results['Lower Level-x'] = np.round(np.array(df_scanner_results['Lower Level']), 5)
df_scanner_results['Range'] = np.round(np.array(df_scanner_results['Total Distance UL']), 5)

datatable = df_scanner_results[['Currency', '15m', '1h', '4h', '1d', 'FX Score','Upper Level-x','Lower Level-x','Range', 'SR Filter']]
source = ColumnDataSource(datatable)
now = datetime.now().strftime("%H:%M %m/%d/%Y")
msg = 'FX Sentiments as of ' + now + '.'

msg = 'FX Sentiments as of ' + now + '.'

columns = [
        TableColumn(field="Currency", title=now, formatter=StringFormatter()),
        TableColumn(field="15m", title="15Minutes"),
        TableColumn(field="1h", title="1Hour"),
        TableColumn(field="4h", title="4Hours"),
        TableColumn(field="1d", title="1Day"), 
        TableColumn(field="FX Score", title="FX Score"), 
        TableColumn(field="Upper Level-x", title="Upper Level"),
        TableColumn(field="Lower Level-x", title="Lower Level"),
        TableColumn(field="Range", title="Range (points)"),
        TableColumn(field="SR Filter", title="SR Filter")
    ]
data_table = DataTable(source=source, columns=columns, width=len(df_pairs.columns)*150, height=((len(df_pairs)+2)*28))
try:
    save(data_table, title='Trend Scanner', filename=(home +'\Desktop\signals.html'))
except:
    print(data_table)

telegram_bot_sendtext(msg)
try:
    telegram_bot_sendfile('signals.html')
except:
    print('Data table failed.')

df_watchlist = df_pairs_filtered[(df_pairs_filtered['SR Filter'] != 'NEUTRAL') & (df_pairs_filtered['FX Score converted'] > 3)]
columns = ['Currency', 'FX Score', 'Lower Level', 'Upper Level', 'SR Filter']
df_watchlist_final = df_watchlist[columns][df_watchlist['SR Filter'].str.contains('WATCHLIST')]
df_watchlist_old = pd.read_csv(home+'\Desktop\Experimental\/fx_watchlist.csv')
df_watchlist_old = df_watchlist_old.append(df_watchlist_final)
df_watchlist_old.drop_duplicates(subset=['Currency'], keep='last', inplace=True)
df_watchlist_old.to_csv(home+'\Desktop\Experimental\/fx_watchlist.csv', index=False)
telegram_bot_sendtext('Saved watchlist.')   
print('done')