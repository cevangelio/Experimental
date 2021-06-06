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

api_key = 'c1iobuf48v6vit2166cg'
finnhub_client = finnhub.Client(api_key=api_key)

avoid = [0,1,5,6] #not trading on Monday, Tuesday, Saturday, Sunday
if datetime.now().weekday() in avoid:
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

def telegram_bot_sendfile():
    url = "https://api.telegram.org/bot" + bot_token + "/sendDocument"
    files = {'document': open((home +'\Desktop\signals.html'), 'rb')}
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

def sentiment_score(data):
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

def dirxn(fx_score):
    if fx_score < 0:
        return 'sell'
    elif fx_score > 0:
        return 'buy'

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
    lower = levels[levels.index(current_price)-1]
    return lower

def upper_level(current_price, levels):
    levels.append(current_price)
    levels.sort()
    upper = levels[levels.index(current_price)+2]
    return upper

fx_pairs = []
fx_raw =  ['ac', 'af', 'aj', 'au', 'cf', 'cj', 'ea', 'ec', 'ef', 'ej', 'eu', 'fj', 'ga', 'gc', 'gf', 'gj', 'gu', 'nc', 'nj', 'nu', 'uc', 'uf', 'uj']
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

### df to table/img

datatable = df_pairs
source = ColumnDataSource(datatable)
now = datetime.now().strftime("%H:%M %m/%d/%Y")
msg = 'FX Sentiments as of ' + now + '.'

columns = [
        TableColumn(field="Currency", title=now, formatter=StringFormatter()),
        TableColumn(field="15m", title="15Minutes"),
        TableColumn(field="1h", title="1Hour"),
        TableColumn(field="4h", title="4Hours"),
        TableColumn(field="1d", title="1Day"), 
        TableColumn(field="FX Score", title="FX Score")
    ]
data_table = DataTable(source=source, columns=columns, width=len(df_pairs.columns)*120, height=((len(df_pairs)+2)*28))
try:
    save(data_table, title='Trend Scanner', filename=(home +'\Desktop\signals.html'))
except:
    print(data_table)

telegram_bot_sendtext(msg)
try:
    telegram_bot_sendfile()
except:
    print('Data table failed.')

if ((datetime.now().weekday() == 2) and (datetime.now().hour == 6)): #Wednesday 6am
    exit()
else:
    pass

if ((datetime.now().hour == 21) and (datetime.now().weekday() < 4)) or ((datetime.now().hour == 6) and (datetime.now().weekday() !=0)):
    pass
else:
    exit()

#filter high value pairs
df_pairs_filtered = df_pairs
df_pairs_filtered['FX Score converted'] = np.absolute(df_pairs['FX Score'])
df_pairs_filtered.sort_values(by = ['FX Score converted'], inplace=True, ascending=False)
df_pairs_filtered.reset_index(inplace=True)
df_pairs_filtered.drop(columns = ['index'], inplace=True)
df_pairs_filtered = df_pairs_filtered[df_pairs_filtered['FX Score converted'] > 5] #get only above 6
above_six_pairs = len(df_pairs_filtered)

## News high impact filter

fx_calendar = pd.read_csv(home+'\Desktop\Fx_calendar_2b_raw.csv')
today = datetime.now()
curr_to_avoid_raw = fx_calendar['Currency'][(fx_calendar['Date']==today.strftime('%m/%d/%Y')) & (fx_calendar['Time']>today.strftime('%H:%M'))]
curr_to_avoid = list(set(list(curr_to_avoid_raw)))

has_news = []
for currency in curr_to_avoid:
    for pair in df_pairs_filtered['Currency']:
        if currency in pair:
            has_news.append(pair)
news_point = [] #1 point if there is news
time_point = [] #1 point if more than 8 hours To be coded.
for pair in df_pairs_filtered['Currency']:
    if pair in has_news:
        news_point.append(1)
    else:
        news_point.append(0)

## Create a time filter if past time already, can trade

df_pairs_filtered['News point'] = news_point
df_pairs_filtered = df_pairs_filtered[df_pairs_filtered['News point'] == 0]
df_pairs_filtered.reset_index(inplace=True)
no_news_pairs = len(df_pairs_filtered)

#detect duplicate

top_pair = df_pairs_filtered.loc[0]['Currency']
potential_second = list(df_pairs_filtered['Currency'][1:])
for pair in potential_second:
    result = detect_duplicate(top_pair, pair)
    if result == True:
        potential_second.remove(pair)

df_pairs_to_trade = pd.DataFrame(columns=['Currency', 'Direction'])
df_pairs_to_trade.loc[0] = [top_pair, dirxn(df_pairs_filtered.loc[0]['FX Score'])]

if len(potential_second) >= 1:
    second_pair = potential_second[0]
    second_pair_fx_score = df_pairs_filtered['FX Score'][df_pairs_filtered['Currency'] == potential_second[0]].max()
    df_pairs_to_trade.loc[1] = [second_pair, dirxn(second_pair_fx_score)]
else:
    pass

no_duplicate_pairs=(len(potential_second)+1)

get_levels = []
mta.initialize()
volume = 0.01

if len(df_pairs_to_trade) == 0:
    telegram_bot_sendtext("No trades made. High impact news coming.")
    exit()
elif len(df_pairs_to_trade) == 1:
    pair = df_pairs_to_trade['Currency'].loc[0]
    get_levels.append(pair)
    dirxn = df_pairs_to_trade['Direction'].loc[0]
    trade(dirxn=dirxn, symbol=pair, volume=volume)
    telegram_bot_sendtext(dirxn.capitalize() + " position opened for " + pair + ".")
else:
    pair1 = df_pairs_to_trade['Currency'].loc[0]
    get_levels.append(pair1)
    pair2 = df_pairs_to_trade['Currency'].loc[1]
    get_levels.append(pair2)
    dirxn1 = df_pairs_to_trade['Direction'].loc[0]
    dirxn2 = df_pairs_to_trade['Direction'].loc[1]
    trade(dirxn=dirxn1, symbol=pair1, volume=volume)
    telegram_bot_sendtext(dirxn1.capitalize() + " position opened for " + pair1 + ".")
    trade(dirxn=dirxn2, symbol=pair2, volume=volume)
    telegram_bot_sendtext(dirxn2.capitalize() + " position opened for " + pair2 + ".")

mta.shutdown()

status_report = str(above_six_pairs) + " pairs are trending.\n" + "Following pairs with high impact news: " + str(curr_to_avoid) + '\n' + str(no_news_pairs) + " pairs with no high impact news. \n" + str(no_duplicate_pairs) + " total tradeable pairs after removing duplicates."
telegram_bot_sendtext(status_report)

##Upper/Lower SR

levels = []
for currency in df_pairs_to_trade['Currency']:
    sr = get_sr(currency, 240)
    levels.append(sr)
    time.sleep(1)

df_pairs_to_trade['Levels'] = levels

df_pairs_to_trade['Current Price'] = [yf.Ticker(pair + "=X").info['bid'] for pair in df_pairs_to_trade['Currency']]

lower_levels = []
upper_levels = []

for pair in df_pairs_to_trade['Currency']:
    current_price = df_pairs_to_trade['Current Price'][df_pairs_to_trade['Currency'] == pair].values[0]
    levels_raw = []
    levels_raw = df_pairs_to_trade['Levels'][df_pairs_to_trade['Currency'] == pair]
    levels = levels_raw.values[0]
    lower_levels.append(lower_level(current_price, levels))
    upper_levels.append(upper_level(current_price, levels))

df_pairs_to_trade['Upper Level'] = upper_levels
df_pairs_to_trade['Lower Level'] = lower_levels

for currency in df_pairs_to_trade['Currency']:
    curr_price = df_pairs_to_trade['Current Price'][df_pairs_to_trade['Currency'] == currency].values[0]
    level_1 = df_pairs_to_trade['Lower Level'][df_pairs_to_trade['Currency'] == currency].values[0]
    level_2 = df_pairs_to_trade['Upper Level'][df_pairs_to_trade['Currency'] == currency].values[0]
    telegram_bot_sendtext(currency + '\nCurrent Price: ' + str(curr_price) + '\nLevel 1: ' + str(round(level_1, 5)) + '\nLevel 2: ' + str(round(level_2, 5)))