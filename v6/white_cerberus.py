'''
Strategy:

1. 3 TF (H1, H4, D1)
2. RSI14 = overbought or oversold
3. RSI100 = Trend

reverse cerberus
buy+overbought = buy
sell+oversold = sell
buy+oversold = sell
sell+overbought = buy

4. All 3 heads of cerberus should agree
5. SL

test commit from vs - - triple test

'''
import numpy as np
import pandas as pd
import requests
import datetime
from datetime import date, datetime
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
if datetime.now().weekday() == 0 and datetime.now().hour < 5:
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

def cerberus(tf='H1'):
    df_raw = pd.DataFrame()
    df_raw['Currency'] = list_symbols
    current_price_l = []
    atr_l = []
    rsi_ov_l = []
    rsi_ov_prev_l = []
    rsi_trend_l = []
    for currency in df_raw['Currency']:
        bars = pd.DataFrame(MT.Get_last_x_bars_from_now(instrument = currency, timeframe = MT.get_timeframe_value(tf), nbrofbars=600))
        current_price = bars['close'].loc[len(bars) - 1]
        current_price_l.append(current_price)
        atr_raw = ta.atr(high = bars['high'], low = bars['low'], close = bars['close'],mamode = 'EMA')
        bars['atr'] = atr_raw
        atr = atr_raw[len(bars) - 1] #last value
        atr_l.append(atr) 
        rsi_raw = ta.rsi(bars['close'], length = 14)
        bars['rsi'] = rsi_raw
        rsi = rsi_raw[len(bars) -1]
        rsi_ov_l.append(rsi)
        rsi_prev = rsi_raw[len(bars) -2]
        rsi_ov_prev_l.append(rsi_prev)
        rsi_trend_raw = ta.rsi(bars['close'], length = 100)
        bars['rsi trend'] = rsi_trend_raw
        rsi_trend = rsi_trend_raw[len(bars)-1]
        rsi_trend_l.append(rsi_trend)
    df_raw['Current Price'] = current_price_l
    df_raw['atr'] = atr_l
    df_raw['rsi'] = rsi_ov_l
    df_raw['rsi prev'] = rsi_ov_prev_l
    df_raw['rsi trend'] = rsi_trend_l
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
        # if 65 <= rsi_status_raw <= 69:
        #     rsi_status.append('overbought')
        # elif 35 >= rsi_status_raw >= 31:
        #     rsi_status.append('oversold')
        # else:
        #     rsi_status.append('ignore')
    df_raw['RSI Status'] = rsi_status
    trade_status = []
    for line in range(0, len(df_raw)):
        if df_raw['RSI Trend'].loc[line] == 'buy' and df_raw['RSI Status'].loc[line] == 'overbought':
            trade_status.append('buy')
        elif df_raw['RSI Trend'].loc[line] == 'sell' and df_raw['RSI Status'].loc[line] == 'oversold':
            trade_status.append('sell')
        elif df_raw['RSI Trend'].loc[line] == 'buy' and df_raw['RSI Status'].loc[line] == 'oversold':
            trade_status.append('sell')
        elif df_raw['RSI Trend'].loc[line] == 'sell' and df_raw['RSI Status'].loc[line] == 'overbought':
            trade_status.append('buy')
        else:
            trade_status.append('ignore')
    df_raw['Action'] = trade_status
    return df_raw

df_final = pd.DataFrame()
df_final['Currency'] = list_symbols

tfs = ['H1','H4','D1']
for tf in tfs:
    df = cerberus(tf=tf)
    print(df)
    df_final['Action ' + tf] = np.array(df['Action'])
    df_final['RSI ' + tf] = np.array(df['RSI Status'])
    df_final['RSI Value ' + tf] = np.array(df['rsi'])
    df_final['RSI Value Prev ' + tf] = np.array(df['rsi prev'])

print(df_final)

df_og = df_final
df_final = df_final[df_final['Action H1'] != 'ignore']
df_final = df_final[df_final['Action H4'] != 'ignore']
to_trade_final = df_final[df_final['Action D1'] != 'ignore']
to_trade_final.reset_index(inplace = True)
to_trade_final.drop(columns = 'index', inplace = True)
print('Filtered ignore currencies.')

for line in range(0, len(to_trade_final)):
    if to_trade_final['Action H1'].loc[line] == to_trade_final['Action H4'].loc[line] == to_trade_final['Action D1'].loc[line]:
        print(to_trade_final['Currency'].loc[line], ' is good.')
    else:
        to_trade_final.drop([line], inplace=True)
print('Filtered disagreeing TFs.')

positions = MT.Get_all_open_positions()
all_pairs = set(list(positions['instrument']))

currs_traded =[]
for currency in to_trade_final['Currency']:
    if currency in all_pairs:
        curr_index = to_trade_final[to_trade_final['Currency'] == currency].index.values[0]
        to_trade_final.drop([curr_index], inplace=True)
        currs_traded.append(currency)

if len(currs_traded) > 0:
    telegram_bot_sendtext(str(currs_traded) + ' are ready to trade from CERBERUS but have exceeded open positions allowed.')

to_trade_final.reset_index(inplace=True)
to_trade_final.drop(columns = 'index', inplace=True)
print('Removed currencies with existing trades.')

for currency in positions['instrument']:
    rsi_close = df_og['RSI Value D1'][df_og['Currency'] == currency].values[0]
    rsi_close_prev = df_og['RSI Value Prev D1'][df_og['Currency'] == currency].values[0]
    pnl = positions['profit'][positions['instrument'] == currency].values[0]
    if positions['position_type'][positions['instrument'] == currency].values[0] == 'sell':
        if rsi_close <= 30:
            if rsi_close_prev < rsi_close:
                MT.Close_position_by_ticket(ticket=positions['ticket'][positions['instrument'] == currency].values[0])
                telegram_bot_sendtext(currency + ' position closed. PNL: ' + str(pnl) + '. RSI value oversold.')
            else:
                pass
    if positions['position_type'][positions['instrument'] == currency].values[0] == 'buy':
        if rsi_close >= 70:
            if rsi_close_prev > rsi_close:
                MT.Close_position_by_ticket(ticket=positions['ticket'][positions['instrument'] == currency].values[0])
                telegram_bot_sendtext(currency + ' position closed. PNL: ' + str(pnl) + '. RSI value bought.')
            else:
                pass   
    else:
      print(currency, ' is okay. ')

for pair in to_trade_final['Currency']:
    dirxn = to_trade_final['Action D1'][to_trade_final['Currency'] == pair].values[0]
    journal_entry = []
    # sloss = to_trade_final['sl'][to_trade_final['Currency'] == pair].values[0]
    # tprof = to_trade_final['tp'][to_trade_final['Currency'] == pair].values[0]
    spread = MT.Get_last_tick_info(instrument=pair)['spread']
    timestmp = datetime.now().strftime('%H:%M')
    magic_num = int(datetime.now().strftime('%Y%m%d%H%M%S'))
    vol = 1
    if spread <= 10.0:
        order = MT.Open_order(instrument=pair, ordertype=dirxn, volume=vol, openprice = 0.0, slippage = 10, magicnumber=magic_num, stoploss=0, takeprofit=0, comment = 'white_cerberus ' + timestmp)
        if order != -1:    
            telegram_bot_sendtext('Cerberus setup found. Position opened successfully: ' + pair + ' (' + dirxn.upper() + ')')
            time.sleep(3)
        else:
            telegram_bot_sendtext('Cerberus setup found. ' + MT.order_return_message + ' for ' + pair + ' (' + dirxn.upper() + ')')
    else:
        telegram_bot_sendtext('Cerberus setup found but spread too high. ' + pair + ' (' + dirxn.upper() + '), spread: ' + str(spread))
