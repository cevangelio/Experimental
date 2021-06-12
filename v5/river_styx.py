#river styx

'''
if above 240ema in 4h - sell, vice versa (countertrend)
entry is oversold (35 and below)/ oversold (65 and above)
exit is reverse of RSI (overbought or oversold)
'''

import numpy as np
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
list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCAD','GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair
con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup=symbols)

home = str(Path.home())
t_gram_creds = open((home+'/Desktop/t_gram.txt'), 'r')
bot_token = t_gram_creds.readline().split('\n')[0]
bot_chatID = t_gram_creds.readline()
t_gram_creds.close()

def telegram_bot_sendtext(bot_message):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

df_raw = pd.DataFrame()
df_raw['Currency'] = list_symbols

current_price_l = []
ema_l = []
macd_l = []
trendline_raw_l = []
rsi_l = []
rsi_trend_l = []
x_bars = 600

for currency in df_raw['Currency']:
    bars = pd.DataFrame(MT.Get_last_x_bars_from_now(instrument = currency, timeframe = MT.get_timeframe_value('H4'), nbrofbars=x_bars))
    current_price = bars['close'].loc[len(bars) - 1]
    current_price_l.append(current_price)
    ema_raw = ta.ema(bars['close'], length = 240)
    bars['ema'] = ema_raw
    ema = ema_raw[len(bars) - 1] #last value
    ema_l.append(ema)
    atr_raw = ta.atr(high = bars['high'], low = bars['low'], close = bars['close'],mamode = 'EMA')
    rsi_raw = ta.rsi(bars['close'], length = 14)
    rsi_trend_raw = ta.rsi(bars['close'], length = 200)
    bars['rsi'] = rsi_raw
    bars['rsi trend'] = rsi_trend_raw
    rsi = rsi_raw[len(bars)-1]
    rsi_l.append(rsi)
    rsi_trend = rsi_trend_raw[len(bars)-1]
    rsi_trend_l.append(rsi_trend)
    trendline_raw = (((bars['ema'].loc[len(bars) - 20]) - (bars['ema'].loc[len(bars) - 1]))/bars['ema'].loc[len(bars) - 1])*100
    trendline_raw_l.append(abs(trendline_raw))

df_raw['Current Price'] = current_price_l
df_raw['EMA240'] = ema_l
df_raw['Trendline Raw'] = trendline_raw_l
df_raw['rsi'] = rsi_l
df_raw['rsi trend'] = rsi_trend_l

styx_trade_logic = []
for pair in df_raw['Currency']:
    if (df_raw['Current Price'][df_raw['Currency'] == pair].values[0] > df_raw['EMA240'][df_raw['Currency'] == pair].values[0]) and (df_raw['rsi'][df_raw['Currency'] == pair].values[0] >= 65) and (df_raw['rsi trend'][df_raw['Currency'] == pair].values[0] < 50):
        styx_trade_logic.append('sell')
    elif (df_raw['Current Price'][df_raw['Currency'] == pair].values[0] < df_raw['EMA240'][df_raw['Currency'] == pair].values[0]) and (df_raw['rsi'][df_raw['Currency'] == pair].values[0] <= 35) and (df_raw['rsi trend'][df_raw['Currency'] == pair].values[0] > 50):
        styx_trade_logic.append('buy')
    else:
        styx_trade_logic.append('ignore')

df_raw['Styx Bias'] = styx_trade_logic
print(df_raw)

to_trade_final = df_raw[df_raw['Styx Bias'] != 'ignore']
positions = MT.Get_all_open_positions()
all_pairs = set(list(positions['instrument']))

currs_traded =[]
for currency in to_trade_final['Currency']:
    if currency in all_pairs:
        curr_index = to_trade_final[to_trade_final['Currency'] == currency].index.values[0]
        to_trade_final.drop([curr_index], inplace=True)
        currs_traded.append(currency)

if len(currs_traded) > 0:
    telegram_bot_sendtext(str(currs_traded) + ' are ready to trade from screener but have exceeded open positions allowed. (STYX)')

to_trade_final.to_csv(home + '/Desktop/Experimental/v5/to_trade_final_styx.csv')

if len(to_trade_final) == 0:
    telegram_bot_sendtext('Styx no valid trade.')

for pair in to_trade_final['Currency']:
    dirxn = to_trade_final['Styx Bias'][to_trade_final['Currency'] == pair].values[0]
    sloss = 0 #to_trade_final['sl'][to_trade_final['Currency'] == pair].values[0]
    tprof = 0 #to_trade_final['tp'][to_trade_final['Currency'] == pair].values[0]
    spread = MT.Get_last_tick_info(instrument=pair)['spread']
    timestmp = datetime.now().strftime('%H:%M')
    vol = 1
    if spread <= 10.0:
        try:
            MT.Open_order(instrument=pair, ordertype=dirxn, volume=vol, openprice = 0.0, slippage = 10, magicnumber=41, stoploss=sloss, takeprofit=tprof, comment = 'styx ' + timestmp)
            telegram_bot_sendtext('Styx valid setup found. Position opened successfully: ' + pair + ' (' + dirxn.upper() + ')')
            time.sleep(3)
        except Exception as e:
            telegram_bot_sendtext('Valid setup found. Error opening position: ' + pair + ' (' + dirxn.upper() + ')')
            telegram_bot_sendtext(str(e))
    else:
        telegram_bot_sendtext('Styx valid setup found but spread too high. ' + pair + ' (' + dirxn.upper() + '), spread: ' + str(spread))
