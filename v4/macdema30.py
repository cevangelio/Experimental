#macd 30mins

'''
to do:
2. add filter for spread too high

obs:
1. Start trading Monday 5pm only -any signal before is shit
'''

from numpy import append
import pandas as pd
import requests
import datetime
from datetime import datetime
import time
from pathlib import Path
import pandas_ta as ta
from get_signal import *
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
port = 1122 #FXCM MAIN 50k 1:100
list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair
con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup=symbols)

if datetime.now().weekday() > 4: #don't run on weekends
    exit()
elif datetime.now().weekday() == 0 and datetime.now().hour < 17:
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

df_raw = pd.DataFrame()
df_raw['Currency'] = list_symbols

current_price_l = []
ema_l = []
macd_l = []
macd_signal_l = []
macd_prev_l = []
macd_signal_prev_l = []
trendline_raw_l = []
atr_l = []
x_bars = 600
for currency in df_raw['Currency']:
    bars = pd.DataFrame(MT.Get_last_x_bars_from_now(instrument = currency, timeframe = MT.get_timeframe_value('M30'), nbrofbars=x_bars))
    print(len(bars))
    current_price = bars['close'].loc[len(bars) - 1]
    current_price_l.append(current_price)
    ema_raw = ta.ema(bars['close'], length = 200)
    bars['ema'] = ema_raw
    ema = ema_raw[len(bars) - 1] #last value
    ema_l.append(ema)
    atr_raw = ta.atr(high = bars['high'], low = bars['low'], close = bars['close'],mamode = 'EMA')
    bars['atr'] = atr_raw
    atr = atr_raw[len(bars) - 1] #last value
    atr_l.append(atr) #create logic to + 2ATR if buy, -2ATR if sell
    macd_raw = ta.macd(bars['close'])
    macd_final = pd.concat([bars,macd_raw], axis=1, join='inner')
    macd_curr = macd_final.loc[len(bars) - 1]['MACD_12_26_9']
    macd_l.append(macd_curr)
    macd_signal_curr = macd_final.loc[len(bars) - 1]['MACDs_12_26_9']
    macd_signal_l.append(macd_signal_curr)
    macd_prev = macd_final.loc[len(bars) - 6]['MACD_12_26_9']
    macd_prev_l.append(macd_prev)
    macd_signal_prev = macd_final.loc[len(bars) - 6]['MACDs_12_26_9']
    macd_signal_prev_l.append(macd_signal_prev)
    trendline_raw = (((bars['ema'].loc[len(bars) - 72]) - (bars['ema'].loc[len(bars) - 1]))/bars['ema'].loc[len(bars) - 1])*100
    trendline_raw_l.append(abs(trendline_raw))

df_raw['Current Price'] = current_price_l
df_raw['EMA200'] = ema_l
df_raw['Trendline Raw'] = trendline_raw_l
df_raw['MACD'] = macd_l
df_raw['MACD SIGNAL'] = macd_signal_l
df_raw['MACD PREV'] = macd_prev_l
df_raw['MACD SIGNAL PREV'] = macd_signal_prev_l
df_raw['atr'] = atr_l

trend = []
for line in range(0, len(df_raw)):
    if df_raw['Current Price'].loc[line] > df_raw['EMA200'].loc[line]:
        trend.append('buy')
    elif df_raw['Current Price'].loc[line] < df_raw['EMA200'].loc[line]:
        trend.append('sell')
    else:
        trend.append('ignore')
df_raw['Trend'] = trend

trendline = []
for line in range(0, len(df_raw)):
    if df_raw['Trendline Raw'].loc[line] < 0.1:
        trendline.append('flat')
    elif df_raw['Trendline Raw'].loc[line] >= 0.1:
        trendline.append('sloped')
    else:
        trendline.append('ignore')
df_raw['Trendline'] = trendline

macd_prev_trend = []
macd_trend = []

for line in range(0, len(df_raw)):
    if df_raw['MACD'].loc[line] < 0 and df_raw['MACD SIGNAL'].loc[line] < 0:
        if df_raw['MACD'].loc[line] > df_raw['MACD SIGNAL'].loc[line]:
            macd_trend.append('buy')
        elif df_raw['MACD'].loc[line] < df_raw['MACD SIGNAL'].loc[line]:
            macd_trend.append('sell')
        else:
            macd_trend.append('ignore')
    else:
        macd_trend.append('ignore')
df_raw['Current MACD Trend'] = macd_trend

for line in range(0, len(df_raw)):
    if df_raw['MACD PREV'].loc[line] < 0 and df_raw['MACD SIGNAL PREV'].loc[line] < 0:
        if df_raw['MACD PREV'].loc[line] > df_raw['MACD SIGNAL PREV'].loc[line]:
            macd_prev_trend.append('buy')
        elif df_raw['MACD PREV'].loc[line] < df_raw['MACD SIGNAL PREV'].loc[line]:
            macd_prev_trend.append('sell')
        else:
            macd_prev_trend.append('ignore')
    else:
        macd_prev_trend.append('ignore')
df_raw['Previous MACD Trend'] = macd_trend

atr_away = []
for line in range(0, len(df_raw)):
    if df_raw['Trend'].loc[line] == 'buy':
        dist_away_ema = df_raw['Current Price'].loc[line] - 2*df_raw['atr'].loc[line]
        if dist_away_ema > df_raw['EMA200'].loc[line]:
            atr_away.append('buy')
        else:
            atr_away.append('ignore')
    elif df_raw['Trend'].loc[line] == 'sell':
        dist_away_ema = df_raw['Current Price'].loc[line] + 2*df_raw['atr'].loc[line]
        if dist_away_ema < df_raw['EMA200'].loc[line]:
            atr_away.append('sell')
        else:
            atr_away.append('ignore')
    else:
        atr_away.append('ignore')
df_raw['ATR Away'] = atr_away

df_raw.to_csv(home+'/Desktop/Experimental/v4/macdema_test.csv')
telegram_bot_sendfile(filename='macdema_test.csv', location=home+'/Desktop/Experimental/v4/')

#Filter to trade df
to_trade_raw = df_raw[df_raw['Current MACD Trend'] != 'ignore']
to_trade_raw.reset_index(inplace = True)
to_trade_raw.drop(columns = 'index', inplace = True)
# #rules

trade = []
# for line in range(0, len(to_trade_raw)):
#     if to_trade_raw['Trend'].loc[line] == 'sell' and to_trade_raw['Previous MACD Trend'].loc[line] == 'buy' and to_trade_raw['Current MACD Trend'].loc[line] == 'sell':
#         trade.append('valid sell')
#     elif to_trade_raw['Trend'].loc[line] == 'buy' and to_trade_raw['Previous MACD Trend'].loc[line] == 'sell' and to_trade_raw['Current MACD Trend'].loc[line] == 'buy':
#         trade.append('valid buy')
#     else:
#         trade.append('not valid setup')

for line in range(0, len(to_trade_raw)):
    if to_trade_raw['Trend'].loc[line] == 'sell' and to_trade_raw['Previous MACD Trend'].loc[line] == 'sell' and to_trade_raw['Current MACD Trend'].loc[line] == 'sell' and to_trade_raw['Trendline'].loc[line] == 'sloped' and to_trade_raw['ATR Away'].loc[line] == 'sell':
        trade.append('valid sell')
    elif to_trade_raw['Trend'].loc[line] == 'buy' and to_trade_raw['Previous MACD Trend'].loc[line] == 'buy' and to_trade_raw['Current MACD Trend'].loc[line] == 'buy' and to_trade_raw['Trendline'].loc[line] == 'sloped' and to_trade_raw['ATR Away'].loc[line] == 'buy':
        trade.append('valid buy')
    else:
        trade.append('not valid setup')
to_trade_raw['Action'] = trade
print(to_trade_raw)

to_trade_final = to_trade_raw[to_trade_raw['Action'] != 'not valid setup']
sl = []
tp = []
to_trade_final.reset_index(inplace=True)
to_trade_final.drop(columns = 'index', inplace=True)
for line in range(0, len(to_trade_final)):
    if to_trade_final['Trend'].loc[line] == 'sell':
        sl_raw = to_trade_final['Current Price'].loc[line] + 2.1*to_trade_final['atr'].loc[line]
        sl.append(sl_raw)
        tp_raw = to_trade_final['Current Price'].loc[line] - 3*to_trade_final['atr'].loc[line]
        tp.append(tp_raw)
    elif to_trade_final['Trend'].loc[line] == 'buy':
        sl_raw = to_trade_final['Current Price'].loc[line] - 2.1*to_trade_final['atr'].loc[line]
        sl.append(sl_raw)
        tp_raw = to_trade_final['Current Price'].loc[line] + 3*to_trade_final['atr'].loc[line]
        tp.append(tp_raw)
    else:
        sl.append(0)
        tp.append(0)
to_trade_final['sl'] = sl
to_trade_final['tp'] = tp

positions = MT.Get_all_open_positions()
all_pairs = set(list(positions['instrument']))

currs_traded =[]
for currency in to_trade_final['Currency']:
    if currency in all_pairs:
        curr_index = to_trade_final[to_trade_final['Currency'] == currency].index.values[0]
        to_trade_final.drop([curr_index], inplace=True)
        currs_traded.append(currency)

if len(currs_traded) > 0:
    telegram_bot_sendtext(str(currs_traded) + ' are ready to trade from screener but have exceeded open positions allowed.')

to_trade_final.reset_index(inplace=True)
to_trade_final.drop(columns = 'index', inplace=True)
print(to_trade_final)

for currency in positions['instrument']:
    new_sig, macd_trend, prev_macd_trend = get_signal(currency, tf='M30') 
    prev_sig = positions['position_type'][positions['instrument'] == currency].values[0]
    if new_sig != prev_sig:
        MT.Close_position_by_ticket(ticket=positions['ticket'][positions['instrument'] == currency].values[0])
        telegram_bot_sendtext(currency + ' position closed due to change in signal.')
    else:
        print(currency, ' is okay. ', prev_sig, ' ', new_sig)

if len(to_trade_final) == 0:
    telegram_bot_sendtext('No valid setup found.')
    exit()
else:
    pass

for pair in to_trade_final['Currency']:
    dirxn = to_trade_final['Trend'][to_trade_final['Currency'] == pair].values[0]
    sloss = to_trade_final['sl'][to_trade_final['Currency'] == pair].values[0]
    tprof = to_trade_final['tp'][to_trade_final['Currency'] == pair].values[0]
    vol = 1.0
    try:
        MT.Open_order(instrument=pair, ordertype=dirxn, volume=vol, openprice = 0.0, slippage = 10, magicnumber=41, stoploss=sloss, takeprofit=tprof, comment = 'MACDEMA TEST v4b')
        telegram_bot_sendtext('Valid setup found. Position opened successfully: ' + pair + ' (' + dirxn.upper() + ')')
        time.sleep(3)
    except Exception as e:
        telegram_bot_sendtext('Valid setup found. Error opening position: ' + pair + ' (' + dirxn.upper() + ')')
        telegram_bot_sendtext(str(e))