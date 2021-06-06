'''
to do:
1. excessive spread filter

'''
from numpy import e
import pandas as pd
import time
import pandas_ta as ta
import datetime
from datetime import datetime
import requests
from pathlib import Path
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
port = 1125 #FXCM MAIN 50k 1:100
# list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
list_symbols = ['GBPUSD', 'USDCHF', 'GBPCHF', 'EURUSD', 'EURCHF']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair

con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup=symbols)

home = str(Path.home())
t_gram_creds = open((home+'/Desktop/t_gram_cerberus.txt'), 'r')
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

def reverse_trade(type):
    if type == 'sell':
        return 'buy'
    elif type == 'buy':
        return 'sell'

df_raw = pd.DataFrame()
df_raw['Currency'] = ['EURUSD', 'USDCHF', 'EURCHF']

current_price_l = []
ema_l = []
x_bars = 600
for currency in df_raw['Currency']:
    bars = pd.DataFrame(MT.Get_last_x_bars_from_now(instrument = currency, timeframe = MT.get_timeframe_value('H1'), nbrofbars=x_bars))
    current_price = bars['close'].loc[len(bars) - 1]
    current_price_l.append(current_price)
    ema_raw = ta.ema(bars['close'], length = 200)
    bars['ema'] = ema_raw
    ema = ema_raw[len(bars) - 1] #last value
    ema_l.append(ema)

df_raw['Current Price'] = current_price_l
df_raw['EMA'] = ema_l

trend = []
for line in range(0, len(df_raw)):
    if df_raw['Current Price'].loc[line] > df_raw['EMA'].loc[line]:
        trend.append('buy')
    elif df_raw['Current Price'].loc[line] < df_raw['EMA'].loc[line]:
        trend.append('sell')
    else:
        trend.append('ignore')

df_raw['Trend'] = trend

test_1 = abs((np.array(df_raw['Current Price']) - np.array(df_raw['EMA']))/np.array(df_raw['EMA']))*1000

df_raw['str_test_1'] = test_1

df_raw.sort_values(by =['str_test_1'], ascending = False, inplace=True)
df_raw.reset_index(inplace=True)
df_raw.drop(columns = 'index', inplace=True)


pair_spreads = [(MT.Get_last_tick_info(instrument=pair)['spread']) for pair in df_raw['Currency']]
total_spread = np.array(pair_spreads).sum()
print(total_spread)
print(df_raw)

top_pair = df_raw['Currency'].loc[0]
top_pair_trend = ''
if df_raw['Current Price'].loc[0] > df_raw['EMA'].loc[0]:
    top_pair_trend = 'buy'
elif df_raw['Current Price'].loc[0] < df_raw['EMA'].loc[0]:
    top_pair_trend = 'sell'
else:
    top_pair_trend = 'error'

timestmp = datetime.now().strftime('%H:%M')
lot_factor = .0001
profit_factor = .01
vol = round((MT.Get_dynamic_account_info()['balance'])*lot_factor,2)

if top_pair == 'EURCHF':
    try:
        MT.Open_order(instrument='EURCHF', ordertype= top_pair_trend, volume=vol, openprice = 0.0, slippage = 10, magicnumber=41, stoploss=0, takeprofit=0, comment = 'cerberus ' + timestmp)
        time.sleep(1)
        MT.Open_order(instrument='EURUSD', ordertype= reverse_trade(top_pair_trend), volume=vol, openprice = 0.0, slippage = 10, magicnumber=41, stoploss=0, takeprofit=0, comment = 'cerberus ' + timestmp)
        MT.Open_order(instrument='USDCHF', ordertype= reverse_trade(top_pair_trend), volume=vol, openprice = 0.0, slippage = 10, magicnumber=41, stoploss=0, takeprofit=0, comment = 'cerberus ' + timestmp)
        telegram_bot_sendtext('New basket opened. Lead: ' + top_pair + ' , direction: ' + top_pair_trend)
    except:
        error = MT.order_return_message
        telegram_bot_sendtext('Error opening basket. ', error)
elif top_pair == 'EURUSD':
    try:
        MT.Open_order(instrument='EURUSD', ordertype= top_pair_trend, volume=vol, openprice = 0.0, slippage = 10, magicnumber=41, stoploss=0, takeprofit=0, comment = 'cerberus ' + timestmp)
        time.sleep(1)
        MT.Open_order(instrument='EURCHF', ordertype= reverse_trade(top_pair_trend), volume=vol, openprice = 0.0, slippage = 10, magicnumber=41, stoploss=0, takeprofit=0, comment = 'cerberus ' + timestmp)
        time.sleep(1)
        MT.Open_order(instrument='USDCHF', ordertype= top_pair_trend, volume=vol, openprice = 0.0, slippage = 10, magicnumber=41, stoploss=0, takeprofit=0, comment = 'cerberus ' + timestmp)
        telegram_bot_sendtext('New basket opened. Lead: ' + top_pair + ' , direction: ' + top_pair_trend)
    except:
        error = MT.order_return_message
        telegram_bot_sendtext('Error opening basket. ', error)
elif top_pair == 'USDCHF':
    try:
        MT.Open_order(instrument='EURUSD', ordertype= top_pair_trend, volume=vol, openprice = 0.0, slippage = 10, magicnumber=41, stoploss=0, takeprofit=0, comment = 'cerberus ' + timestmp)
        time.sleep(1)
        MT.Open_order(instrument='EURCHF', ordertype= reverse_trade(top_pair_trend), volume=vol, openprice = 0.0, slippage = 10, magicnumber=41, stoploss=0, takeprofit=0, comment = 'cerberus ' + timestmp)
        time.sleep(1)
        MT.Open_order(instrument='USDCHF', ordertype= top_pair_trend, volume=vol, openprice = 0.0, slippage = 10, magicnumber=41, stoploss=0, takeprofit=0, comment = 'cerberus ' + timestmp)
        telegram_bot_sendtext('New basket opened. Lead: ' + top_pair + ' , direction: ' + top_pair_trend)
    except:
        error = MT.order_return_message
        telegram_bot_sendtext('Error opening basket. ', error)