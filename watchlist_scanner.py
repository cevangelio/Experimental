#run every hour starting 7am

import pandas as pd
import time
from pathlib import Path
import finnhub
import yfinance as yf
import requests
import numpy as np
import datetime
from datetime import datetime, timedelta
from bokeh.io import output_file, show, save
from bokeh.layouts import widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, StringFormatter, TableColumn
from bokeh.models import Title
import get_senti as gs
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
port = 1122 #FTMO MAIN

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

def telegram_bot_sendfile(filename):
    url = "https://api.telegram.org/bot" + bot_token + "/sendDocument"
    files = {'document': open((home +'\Desktop' + '\/' + filename), 'rb')}
    data = {'chat_id' : bot_chatID}
    r= requests.post(url, files=files, data=data)
    print(r.status_code, r.reason, r.content)

def trade(dirxn, symbol, volume=0.01, sl=0, tp=0, comment=''):
    con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup={symbol:symbol})
    new_order = MT.Open_order(instrument=symbol, ordertype=dirxn, volume=volume, openprice = 0.0, slippage = 10, magicnumber=41, stoploss=0.0, takeprofit=0.0, comment = comment)
    if new_order > 0:
        return "Order opened for " + symbol + " (" + dirxn.capitalize() + ")."
    else:
        return "Order opening for " + symbol + " failed."

api_key = 'c1iobuf48v6vit2166cg'
finnhub_client = finnhub.Client(api_key=api_key)

watchlist = pd.read_csv(home+'\Desktop\Experimental\/fx_watchlist.csv')
watchlist.drop_duplicates(subset = 'Currency', keep = 'last', inplace=True)
watchlist.reset_index(inplace=True)
watchlist.drop(columns = ['index'], inplace=True)

if len(watchlist) == 0:
    exit()
else:
    pass

watchlist['Current Price'] = [yf.Ticker(pair + "=X").info['bid'] for pair in watchlist['Currency']]
watchlist['Total Distance UL'] = np.array(watchlist['Upper Level']) - np.array(watchlist['Lower Level'])
watchlist['% Away Lower'] = (np.array(watchlist['Current Price']) - np.array(watchlist['Lower Level']))/np.array(watchlist['Total Distance UL'])
watchlist['% Away Upper'] = (np.array(watchlist['Upper Level']) - np.array(watchlist['Current Price']))/np.array(watchlist['Total Distance UL'])

watchlist.drop(columns = 'FX Score', inplace=True)
watchlist['FX Score'] = [gs.sentiment_score(currency) for currency in watchlist['Currency']]

sr_filter = []

for pair in watchlist['Currency']:
    if (watchlist['FX Score'][watchlist['Currency'] == pair].values[0] <= -4) and (0 <= watchlist['% Away Upper'][watchlist['Currency'] == pair].values[0] <= 0.10):
        sr_filter.append('BUY')
    elif (watchlist['FX Score'][watchlist['Currency'] == pair].values[0] <= -4) and (0.11 <= watchlist['% Away Upper'][watchlist['Currency'] == pair].values[0] <= 0.4):
        sr_filter.append('BUY WATCHLIST')
    elif (watchlist['FX Score'][watchlist['Currency'] == pair].values[0] <= -4) and (0.80 <= watchlist['% Away Upper'][watchlist['Currency'] == pair].values[0] <= 1):
        sr_filter.append('BUY WATCHLIST')
    elif (watchlist['FX Score'][watchlist['Currency'] == pair].values[0] >= 4) and (0 <= watchlist['% Away Lower'][watchlist['Currency'] == pair].values[0] <= 0.10):
        sr_filter.append('SELL')
    elif (watchlist['FX Score'][watchlist['Currency'] == pair].values[0] >= 4) and (0.11 <= watchlist['% Away Lower'][watchlist['Currency'] == pair].values[0] <= 0.40):
        sr_filter.append('SELL WATCHLIST')
    elif (watchlist['FX Score'][watchlist['Currency'] == pair].values[0] >= 4) and (0.80 <= watchlist['% Away Lower'][watchlist['Currency'] == pair].values[0] <= 1):
        sr_filter.append('SELL WATCHLIST')
    else:
        sr_filter.append('NEUTRAL')

watchlist['Current State'] = sr_filter

datatable = watchlist
source = ColumnDataSource(datatable)
now = datetime.now().strftime("%H:%M %m/%d/%Y")

columns = [
        TableColumn(field="Currency", title=now, formatter=StringFormatter()),
        TableColumn(field="FX Score", title="FX Score"),
        TableColumn(field="Lower Level", title="Lower Level"),
        TableColumn(field="Upper Level", title="Upper Level"),
        TableColumn(field="SR Filter", title="OG State"), 
        TableColumn(field="Current State", title="Current State")
    ]
data_table = DataTable(source=source, columns=columns, width=len(watchlist.columns)*100, height=((len(watchlist)+2)*28))
try:
    save(data_table, title='Watchlist Scanner', filename=(home +'\Desktop\signals_scanner.html'))
except:
    print(data_table)

ready_to_trade = watchlist[['Currency', 'Current State']][(watchlist['Current State'] == 'BUY') | (watchlist['Current State'] == 'SELL')]
print(ready_to_trade)

if len(ready_to_trade) > 0:
    telegram_bot_sendfile('signals_scanner.html')
    for currency in ready_to_trade['Currency']:
        dirxn = watchlist['Current State'][watchlist['Currency'] == currency].values[0]
        msg = now + '\n' + currency + ' is ready to trade from watchlist. (' + dirxn + ')\n'
        telegram_bot_sendtext(msg)
        try:
            trade(dirxn=dirxn.lower(),symbol=currency,volume=2, sl=0, tp=0)
            telegram_bot_sendtext('Position opened successfully: ' + currency + ' (' + dirxn.upper() + ')')
        except:
            telegram_bot_sendtext('Error opening position: ' + currency + ' (' + dirxn.upper() + ')')
        curr_index = watchlist[watchlist['Currency'] == currency].index.values[0]
        watchlist.drop([curr_index], inplace=True)
else:
    telegram_bot_sendtext('No trades from watchlist.')

#Update Watchlist

watchlist_to_save = watchlist[['Currency','FX Score','Lower Level','Upper Level','SR Filter']]
watchlist_to_save.to_csv(home+'\Desktop\Experimental\/fx_watchlist.csv', index=False)