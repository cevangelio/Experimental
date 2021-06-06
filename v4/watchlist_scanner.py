#Watchlist Scanner v3

import pandas as pd
from pathlib import Path
import finnhub
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

def telegram_bot_sendfile(filename):
    url = "https://api.telegram.org/bot" + bot_token + "/sendDocument"
    files = {'document': open(filename, 'rb')}
    data = {'chat_id' : bot_chatID}
    r= requests.post(url, files=files, data=data)
    print(r.status_code, r.reason, r.content)

def trade(dirxn, symbol, volume=0.01, sl=0, tp=0, comment=''):
    try:
        con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup={symbol:symbol})
        new_order = MT.Open_order(instrument=symbol, ordertype=dirxn, volume=volume, openprice = 0.0, slippage = 10, magicnumber=41, stoploss=0.0, takeprofit=0.0, comment = comment)
        if new_order > 0:
            return "Order opened for " + symbol + " (" + dirxn.capitalize() + ")."
        else:
            return "Order opening for " + symbol + " failed."
    except:
        telegram_bot_sendtext('Error connecting to MT4.')
  

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

watchlist = pd.read_csv(home + '/Desktop/Experimental/v3/fx_watchlist.csv')
watchlist.drop_duplicates(subset = 'Currency', keep = 'last', inplace=True)
watchlist.reset_index(inplace=True)
watchlist.drop(columns = ['index'], inplace=True)
print('Step 1: Old watchlist opened.')

current_price = []
for currency in watchlist['Currency']:
    raw = MT.Get_last_tick_info(instrument=currency)['bid']
    print(raw, currency)
    current_price.append(raw)

watchlist['Current Price'] = current_price

print('Step 2: Current Price taken from MT4.')

watchlist['Total Distance UL'] = np.array(watchlist['Upper Level']) - np.array(watchlist['Lower Level'])
watchlist['% Away Lower'] = (np.array(watchlist['Current Price']) - np.array(watchlist['Lower Level']))/np.array(watchlist['Total Distance UL'])
watchlist['% Away Upper'] = (np.array(watchlist['Upper Level']) - np.array(watchlist['Current Price']))/np.array(watchlist['Total Distance UL'])
print('Step 3: Upper/Lower calculation done.')

watchlist['FX Score'] = [gs.sentiment_score(currency) for currency in watchlist['Currency']]
print('Step 4: FX Score done.')

sr_filter = []

for pair in watchlist['Currency']:
    if (watchlist['FX Score'][watchlist['Currency'] == pair].values[0] <0) and (0.2 <= watchlist['% Away Upper'][watchlist['Currency'] == pair].values[0] <= 0.30):
        sr_filter.append('SELL')
    elif (watchlist['FX Score'][watchlist['Currency'] == pair].values[0] < 0) and (0.31 <= watchlist['% Away Upper'][watchlist['Currency'] == pair].values[0] <= 0.40):
        sr_filter.append('SELL WATCHLIST')
    elif (watchlist['FX Score'][watchlist['Currency'] == pair].values[0] > 0) and (0.2 <= watchlist['% Away Lower'][watchlist['Currency'] == pair].values[0] <= 0.30):
        sr_filter.append('BUY')
    elif (watchlist['FX Score'][watchlist['Currency'] == pair].values[0] > 0) and (0.31 <= watchlist['% Away Lower'][watchlist['Currency'] == pair].values[0] <= 0.40):
        sr_filter.append('BUY WATCHLIST')
    else:
        sr_filter.append('NEUTRAL')


# for pair in watchlist['Currency']:
#     if 0 <= watchlist['% Away Upper'][watchlist['Currency'] == pair].values[0] <= 0.20:
#         sr_filter.append('BUY')
#     elif 0.21 <= watchlist['% Away Upper'][watchlist['Currency'] == pair].values[0] <= 0.4:
#         sr_filter.append('BUY WATCHLIST')
#     elif 0.80 <= watchlist['% Away Upper'][watchlist['Currency'] == pair].values[0] <= 1:
#         sr_filter.append('BUY WATCHLIST')
#     elif 0 <= watchlist['% Away Lower'][watchlist['Currency'] == pair].values[0] <= 0.20:
#         sr_filter.append('SELL')
#     elif 0.21 <= watchlist['% Away Lower'][watchlist['Currency'] == pair].values[0] <= 0.40:
#         sr_filter.append('SELL WATCHLIST')
#     elif 0.80 <= watchlist['% Away Lower'][watchlist['Currency'] == pair].values[0] <= 1:
#         sr_filter.append('SELL WATCHLIST')
#     else:
#         sr_filter.append('NEUTRAL')

watchlist['Current State'] = sr_filter
print(watchlist)
print('Step 5: NEW SR Filter done.')

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
    save(data_table, title='Watchlist Scanner', filename=(home + '/Desktop/Experimental/v3/signals_scanner.html'))
except:
    print(data_table)
print('Step 6: Created table and sent.')


ready_to_trade = watchlist[['Currency', 'FX Score', 'SR Filter','Total Distance UL', 'Current Price', '% Away Lower', '% Away Upper','Current State']][(watchlist['Current State'] == 'BUY') | (watchlist['Current State'] == 'SELL')]
positions = MT.Get_all_open_positions()
all_pairs = set(list(positions['instrument']))

for currency in ready_to_trade['Currency']:
    if currency in all_pairs:
        curr_index = ready_to_trade[ready_to_trade['Currency'] == currency].index.values[0]
        ready_to_trade.drop([curr_index], inplace=True)
        telegram_bot_sendtext(currency + ' ready to trade from watchlist but has exceeded open positions allowed.')
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
    telegram_bot_sendfile(home + '/Desktop/Experimental/v3/signals_scanner.html')
    for currency in ready_to_trade['Currency']:
        # sl = ready_to_trade['SL'][ready_to_trade['Currency'] == currency].values[0]
        # vol = ready_to_trade['Volume'][ready_to_trade['Currency'] == currency].values[0]
        if (ready_to_trade['Current State'][ready_to_trade['Currency'] == currency].values[0] == 'BUY') and (ready_to_trade['SR Filter'][ready_to_trade['Currency'] == currency].values[0] == 'BUY WATCHLIST') and (ready_to_trade['FX Score'][ready_to_trade['Currency'] == currency].values[0] > 3):
            dirxn = 'buy'
            msg = now + '\n' + currency + ' is ready to trade from watchlist. (' + dirxn + ')\n'
            telegram_bot_sendtext(msg)
            # validation, events = check_news(currency)
            # if validation == True:
            #     telegram_bot_sendtext(currency, ' got no news.', str(events))
            # else:
            #     pass
            try:
                trade(dirxn=dirxn,symbol=currency,volume=vol, sl=0, tp=0)
                telegram_bot_sendtext('Position opened successfully: ' + currency + ' (' + dirxn.upper() + ')')
            except:
                telegram_bot_sendtext('Error opening position: ' + currency + ' (' + dirxn.upper() + ')')
        elif (ready_to_trade['Current State'][ready_to_trade['Currency'] == currency].values[0] == 'SELL') and (ready_to_trade['SR Filter'][ready_to_trade['Currency'] == currency].values[0] == 'SELL WATCHLIST') and (ready_to_trade['FX Score'][ready_to_trade['Currency'] == currency].values[0] < -3):
            dirxn = 'sell'
            msg = now + '\n' + currency + ' is ready to trade from watchlist. (' + dirxn + ')\n'
            telegram_bot_sendtext(msg)
            # validation, events = check_news(currency)
            # if validation == True:
            #     telegram_bot_sendtext(currency, ' got no news.', str(events))
            # else:
            #     pass
            try:
                trade(dirxn=dirxn,symbol=currency,volume=vol, sl=0, tp=0)
                telegram_bot_sendtext('Position opened successfully: ' + currency + ' (' + dirxn.upper() + ')')
            except:
                telegram_bot_sendtext('Error opening position: ' + currency + ' (' + dirxn.upper() + ')')
else:
    telegram_bot_sendtext('No trades from watchlist.')
print('Step 7: Trades sent if any')

for currency in ready_to_trade['Currency']:
    curr_index = watchlist[watchlist['Currency'] == currency].index.values[0]
    watchlist.drop([curr_index], inplace=True)

watchlist_to_save = watchlist[['Currency','FX Score','Lower Level','Upper Level','SR Filter']]
watchlist_to_save.to_csv(home + '/Desktop/Experimental/v3/fx_watchlist.csv', index=False)
print('Step 8: Saved new watchlist.')
