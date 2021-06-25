#macd

'''

strategy:

1. Macd - same setting, only use current when signal below macd
2. 3 bars should be oversold/overbought --- RSI 14 <buy = oversold> <sell = overbought>, RSI 100 <sell below 50, buy above 50>
3. TF = 4h
4. TP = 2.5 ATR or RSI reverse (invisible)
5. SL = SL reverse (invisible)
6. shirt protect

to do:
6. only place limit orders
7. add trade journal

watcher rules
- move sl to BE at 2ATR 
- close half then change tp*5atr or keep at tp*3atr?
- must be able to check news
- close and telegram

'''

import numpy as np
import pandas as pd
import requests
import datetime
from datetime import datetime
import os
import time
from pathlib import Path
import pandas_ta as ta
from get_signal import *
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
port = 1122 #FXCM MAIN 50k 1:100
list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCAD','GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair
con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup=symbols)

if datetime.now().weekday() > 4: #don't run on weekends
    exit()
elif datetime.now().weekday() <=0: #don't run on Mondays
    exit()
elif datetime.now().weekday() == 1 and datetime.now().hour < 17:
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
macd_l = []
macd_signal_l = []
atr_l = []
rsi_ov_l = []
rsi_trend_l = []

x_bars = 600
for currency in df_raw['Currency']:
    bars = pd.DataFrame(MT.Get_last_x_bars_from_now(instrument = currency, timeframe = MT.get_timeframe_value('H1'), nbrofbars=x_bars))
    current_price = bars['close'].loc[len(bars) - 1]
    current_price_l.append(current_price)
    atr_raw = ta.atr(high = bars['high'], low = bars['low'], close = bars['close'],mamode = 'EMA')
    bars['atr'] = atr_raw
    atr = atr_raw[len(bars) - 1] #last value
    atr_l.append(atr) 
    rsi_raw = ta.rsi(bars['close'], length = 14)
    bars['rsi'] = rsi_raw
    rsi = rsi_raw[len(bars)-1]
    rsi_ov_l.append(rsi)
    rsi_trend_raw = ta.rsi(bars['close'], length = 100)
    bars['rsi trend'] = rsi_trend_raw
    rsi_trend = rsi_trend_raw[len(bars)-1]
    rsi_trend_l.append(rsi_trend)
    macd_raw = ta.macd(bars['close'])
    macd_final = pd.concat([bars,macd_raw], axis=1, join='inner')
    macd_curr = macd_final.loc[len(bars) - 1]['MACD_12_26_9']
    macd_l.append(macd_curr)
    macd_signal_curr = macd_final.loc[len(bars) - 1]['MACDs_12_26_9']
    macd_signal_l.append(macd_signal_curr)

df_raw['Current Price'] = current_price_l
df_raw['MACD'] = macd_l
df_raw['MACD SIGNAL'] = macd_signal_l
df_raw['atr'] = atr_l
df_raw['rsi'] = rsi_ov_l
df_raw['rsi trend'] = rsi_trend_l

macd_trend = []
for line in range(0, len(df_raw)):
    if df_raw['MACD'].loc[line] < 0 and df_raw['MACD SIGNAL'].loc[line] < 0:
        if df_raw['MACD'].loc[line] > df_raw['MACD SIGNAL'].loc[line]:
            macd_trend.append('buy')
        else:
            macd_trend.append('ignore')
    elif df_raw['MACD'].loc[line] > 0 and df_raw['MACD SIGNAL'].loc[line] > 0:
        if df_raw['MACD'].loc[line] < df_raw['MACD SIGNAL'].loc[line]:
            macd_trend.append('sell')
        else:
            macd_trend.append('ignore')
    else:
        macd_trend.append('ignore')
df_raw['Current MACD Trend'] = macd_trend

rsi_score = []
for line in range(0, len(df_raw)):
    rsi_score_raw = df_raw['rsi trend'].loc[line]
    if rsi_score_raw > 50:
        rsi_score.append('buy')
    elif rsi_score_raw < 50:
        rsi_score.append('sell')
    else:
        rsi_score.append('ignore')     
df_raw['RSI Trend'] = rsi_score

rsi_status = []
for line in range(0, len(df_raw)):
    rsi_status_raw = df_raw['rsi'].loc[line]
    if rsi_status_raw >= 65:
        rsi_status.append('overbought')
    elif rsi_status_raw <= 35:
        rsi_status.append('oversold')
    else:
        rsi_status.append('ignore')
df_raw['RSI Status'] = rsi_status

#buy+overbought = sell
#sell+oversold = buy
#buy+oversold = buy
#sell+overbought = sell

trade_status = []
for line in range(0, len(df_raw)):
    if df_raw['RSI Trend'].loc[line] == 'buy' and df_raw['RSI Status'].loc[line] == 'overbought':
        trade_status.append('sell')
    elif df_raw['RSI Trend'].loc[line] == 'sell' and df_raw['RSI Status'].loc[line] == 'oversold':
        trade_status.append('buy')
    elif df_raw['RSI Trend'].loc[line] == 'buy' and df_raw['RSI Status'].loc[line] == 'oversold':
        trade_status.append('buy')
    elif df_raw['RSI Trend'].loc[line] == 'sell' and df_raw['RSI Status'].loc[line] == 'overbought':
        trade_status.append('sell')
    else:
        trade_status.append('ignore')
df_raw['Action'] = trade_status


#Filter to trade df
to_trade_raw = df_raw[df_raw['Action'] != 'ignore']
to_trade_raw.reset_index(inplace = True)
to_trade_raw.drop(columns = 'index', inplace = True)
# # #rules

print(to_trade_raw)

# trade = []

# for line in range(0, len(to_trade_raw)):
#     if to_trade_raw['Previous MACD Trend'].loc[line] == 'ignore' and to_trade_raw['Current MACD Trend'].loc[line] == 'sell' and to_trade_raw['RSI Trend'].loc[line] == 'sell':
#         trade.append('sell')
#     elif to_trade_raw['Previous MACD Trend'].loc[line] == 'ignore' and to_trade_raw['Current MACD Trend'].loc[line] == 'buy' and to_trade_raw['RSI Trend'].loc[line] == 'buy':
#         trade.append('buy')
#     else:
#         trade.append('not valid setup')
# to_trade_raw['Action'] = trade
# print(to_trade_raw)
# to_trade_final = to_trade_raw[to_trade_raw['Action'] != 'not valid setup']

# sl = []
# tp = []
# to_trade_final.reset_index(inplace=True)
# to_trade_final.drop(columns = 'index', inplace=True)
# for line in range(0, len(to_trade_final)):
#     if to_trade_final['Action'].loc[line] == 'sell':
#         sl_raw = to_trade_final['Current Price'].loc[line] + 0*to_trade_final['atr'].loc[line]
#         sl.append(sl_raw)
#         tp_raw = to_trade_final['Current Price'].loc[line] - 2.5*to_trade_final['atr'].loc[line]
#         tp.append(tp_raw)
#     elif to_trade_final['Action'].loc[line] == 'buy':
#         sl_raw = to_trade_final['Current Price'].loc[line] - 0*to_trade_final['atr'].loc[line]
#         sl.append(sl_raw)
#         tp_raw = to_trade_final['Current Price'].loc[line] + 2.5*to_trade_final['atr'].loc[line]
#         tp.append(tp_raw)
#     else:
#         sl.append(0)
#         tp.append(0)
# to_trade_final['sl'] = sl
# to_trade_final['tp'] = tp

# positions = MT.Get_all_open_positions()
# all_pairs = set(list(positions['instrument']))

# currs_traded =[]
# for currency in to_trade_final['Currency']:
#     if currency in all_pairs:
#         curr_index = to_trade_final[to_trade_final['Currency'] == currency].index.values[0]
#         to_trade_final.drop([curr_index], inplace=True)
#         currs_traded.append(currency)

# if len(currs_traded) > 0:
#     telegram_bot_sendtext(str(currs_traded) + ' are ready to trade from screener but have exceeded open positions allowed.')

# to_trade_final.reset_index(inplace=True)
# to_trade_final.drop(columns = 'index', inplace=True)
# print(to_trade_final)

# for currency in positions['instrument']:
#     rsi_close = round(df_raw['rsi'][df_raw['Currency'] == currency].values[0], 2)
#     pnl = positions['profit'][positions['instrument'] == currency].values[0]
#     if positions['position_type'][positions['instrument'] == currency].values[0] == 'sell':
#         if rsi_close <= 30:
#             MT.Close_position_by_ticket(ticket=positions['ticket'][positions['instrument'] == currency].values[0])
#             telegram_bot_sendtext(currency + ' position closed. PNL: ' + str(pnl) + '. RSI value oversold. (' + str(rsi_close) +')')
#     if positions['position_type'][positions['instrument'] == currency].values[0] == 'buy':
#         if rsi_close >= 70:
#             MT.Close_position_by_ticket(ticket=positions['ticket'][positions['instrument'] == currency].values[0])
#             telegram_bot_sendtext(currency + ' position closed. PNL: ' + str(pnl) + '. RSI value oversold. (' + str(rsi_close) +')')        
#     else:
#         print(currency, ' is okay. ')

# styx_execute = os.popen('python3 ' + home + '/Desktop/Experimental/v5/river_styx.py').read()

# if len(to_trade_final) == 0:
#     telegram_bot_sendtext('Garuda no valid setup found.')
#     exit()
# else:
#     pass

# for pair in to_trade_final['Currency']:
#     dirxn = to_trade_final['Trend'][to_trade_final['Currency'] == pair].values[0]
#     sloss = to_trade_final['sl'][to_trade_final['Currency'] == pair].values[0]
#     tprof = to_trade_final['tp'][to_trade_final['Currency'] == pair].values[0]
#     spread = MT.Get_last_tick_info(instrument=pair)['spread']
#     timestmp = datetime.now().strftime('%H:%M')
#     vol = 1
#     if spread <= 10.0:
#         try:
#             MT.Open_order(instrument=pair, ordertype=dirxn, volume=vol, openprice = 0.0, slippage = 10, magicnumber=41, stoploss=0, takeprofit=0, comment = 'garuda ' + timestmp)
#             telegram_bot_sendtext('Garuda setup found. Position opened successfully: ' + pair + ' (' + dirxn.upper() + ')')
#             time.sleep(3)
#         except Exception as e:
#             telegram_bot_sendtext('Garuda setup found. Error opening position: ' + pair + ' (' + dirxn.upper() + ')')
#             telegram_bot_sendtext(str(e))
#     else:
#         telegram_bot_sendtext('Garuda setup found but spread too high. ' + pair + ' (' + dirxn.upper() + '), spread: ' + str(spread))

# df_raw.to_csv(home+'/Desktop/Experimental/v5/macdema_test.csv')
# telegram_bot_sendfile(filename='macdema_test.csv', location=home+'/Desktop/Experimental/v5/')
# to_trade_final.to_csv(home + '/Desktop/Experimental/v5/to_trade_final_garuda.csv')


