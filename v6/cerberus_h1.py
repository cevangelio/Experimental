'''
Strategy:

1. TF = H4
2. RSI14 = cross from oversold to normal (vice versa)
3. RSI100 = below50 = sell, above50 = buy
4. MACD

5. SL = 3ATR
6. Exit = overbought or oversold or TP (5ATR) or basketclose (3K)

'''
import pandas as pd
import requests
import datetime
from datetime import date, datetime
import time
from pathlib import Path
import pandas_ta as ta
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
port = 1125 #FXCM MAIN 5k 1:100
list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCAD','GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
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

def cerberus(tf='H1'):
    df_raw = pd.DataFrame()
    df_raw['Currency'] = list_symbols
    current_price_l = []
    atr_l = []
    atr_prev_l = []
    atr_delta_l = []
    rsi_ov_l = []
    rsi_ov_prev_l = []
    rsi_trend_l = []
    rsi_trend_prev_l = []
    macd_l = []
    macd_signal_l = []
    for currency in df_raw['Currency']:
        bars = pd.DataFrame(MT.Get_last_x_bars_from_now(instrument = currency, timeframe = MT.get_timeframe_value(tf), nbrofbars=600))
        current_price = bars['close'].loc[len(bars) - 1]
        current_price_l.append(current_price)
        atr_raw = ta.atr(high = bars['high'], low = bars['low'], close = bars['close'],mamode = 'EMA')
        bars['atr'] = atr_raw
        atr = atr_raw[len(bars) - 2] #last value
        atr_l.append(atr)
        atr_prev = atr_raw[len(bars) - 3]
        atr_prev_l.append(atr_prev)
        atr_delta = ((atr_prev - atr)/atr_prev)*100
        atr_delta_l.append(round(atr_delta, 2))
        rsi_raw = ta.rsi(bars['close'], length = 14)
        bars['rsi'] = rsi_raw
        rsi = rsi_raw[len(bars)-1]
        rsi_ov_l.append(rsi)
        rsi_prev = rsi_raw[len(bars)-2]
        rsi_ov_prev_l.append(rsi_prev)
        rsi_trend_raw = ta.rsi(bars['close'], length = 100)
        bars['rsi trend'] = rsi_trend_raw
        rsi_trend = rsi_trend_raw[len(bars)-1]
        rsi_trend_l.append(rsi_trend)
        rsi_trend_prev = rsi_trend_raw[len(bars)-2]
        rsi_trend_prev_l.append(rsi_trend_prev)
        macd_raw = ta.macd(bars['close'])
        macd_final = pd.concat([bars,macd_raw], axis=1, join='inner')
        macd_curr = macd_final.loc[len(bars) - 1]['MACD_12_26_9']
        macd_l.append(macd_curr)
        macd_signal_curr = macd_final.loc[len(bars) - 2]['MACDs_12_26_9']
        macd_signal_l.append(macd_signal_curr)
    df_raw['Current Price'] = current_price_l
    df_raw['atr'] = atr_l
    df_raw['atr prev'] = atr_prev_l
    df_raw['atr delta'] = atr_delta_l
    df_raw['MACD'] = macd_l
    df_raw['MACD SIGNAL'] = macd_signal_l
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
    df_raw['rsi prev'] = rsi_ov_prev_l
    df_raw['rsi'] = rsi_ov_l
    df_raw['rsi trend prev'] = rsi_trend_prev_l
    df_raw['rsi trend'] = rsi_trend_l
    rsi_trend_logic = []
    for line in range(0, len(df_raw)):
        rsi_score_raw = df_raw['rsi trend'].loc[line]
        if rsi_score_raw > 50:
            rsi_trend_logic.append('buy')
        elif rsi_score_raw < 50:
            rsi_trend_logic.append('sell')
        else:
            rsi_trend_logic.append('ignore')     
    df_raw['RSI 100'] = rsi_trend_logic
    rsi_status = []
    for line in range(0, len(df_raw)):
        rsi_status_raw = df_raw['rsi'].loc[line]
        rsi_status_raw_prev = df_raw['rsi prev'].loc[line]
        if rsi_status_raw_prev >= 70 and rsi_status_raw < 70:
            rsi_status.append('sell')
        elif rsi_status_raw_prev <= 30 and rsi_status_raw > 30:
            rsi_status.append('buy')
        elif rsi_status_raw_prev >= 50 and rsi_status_raw < 50:
            rsi_status.append('sell')
        elif rsi_status_raw_prev <= 50 and rsi_status_raw > 50:
            rsi_status.append('buy')
        else:
            rsi_status.append('ignore')
    df_raw['RSI 14'] = rsi_status
    trade_status = []
    for line in range(0, len(df_raw)):
        if df_raw['RSI 100'].loc[line] == 'buy' and df_raw['RSI 14'].loc[line] == 'buy' and df_raw['Current MACD Trend'].loc[line] == 'buy':
            trade_status.append('buy')
        elif df_raw['RSI 100'].loc[line] == 'sell' and df_raw['RSI 14'].loc[line] == 'sell' and df_raw['Current MACD Trend'].loc[line] == 'sell':
            trade_status.append('sell')
        else:
            trade_status.append('ignore')
    df_raw['Action'] = trade_status
    df_raw['comment'] = [('CBRUS_v2_'+df_raw['Currency'].loc[line]+datetime.now().strftime('%Y%m%d%H%M%S')) for line in range(0, len(df_raw))]
    sl = []
    tp = []
    for line in range(0, len(df_raw)):
        if df_raw['Action'].loc[line] == 'buy':
            sl.append((df_raw['Current Price'].loc[line]) - (3.3*(df_raw['atr'].loc[line])))
            tp.append((df_raw['Current Price'].loc[line]) + (5*(df_raw['atr'].loc[line])))
        elif df_raw['Action'].loc[line] == 'sell':
            sl.append((df_raw['Current Price'].loc[line]) + (3.3*(df_raw['atr'].loc[line])))
            tp.append((df_raw['Current Price'].loc[line]) - (5*(df_raw['atr'].loc[line])))
        else:
            sl.append(0)
            tp.append(0)
    df_raw['sl'] = sl
    df_raw['tp'] = tp
    df_raw['spread'] = [MT.Get_last_tick_info(instrument=pair)['spread'] for pair in df_raw['Currency']]
    return df_raw

if datetime.now().weekday() > 5: #don't run on weekends
    exit()
elif datetime.now().weekday() == 5 and datetime.now().hour > 5: #last saturday 5am
    exit()
elif datetime.now().weekday() == 0 and datetime.now().hour < 5:
    exit()
else:
    pass

df_final = pd.DataFrame()
df_final['Currency'] = list_symbols

df_final = cerberus(tf='H1')
print(df_final)
df_final.to_csv('d:/TradeJournal/cerberus_raw_h1.csv', index=False)
telegram_bot_sendfile('cerberus_raw_h1.csv',location='d:/TradeJournal/')

df_og = df_final
to_trade_final_raw = df_final[df_final['Action'] != 'ignore']
to_trade_final_raw.reset_index(inplace = True)
to_trade_final_raw.drop(columns = 'index', inplace = True)
to_trade_final_raw.to_csv('d:/TradeJournal/tempo_list_h1.csv', index=False)
to_trade_final = pd.read_csv('d:/TradeJournal/tempo_list_h1.csv')

positions = MT.Get_all_open_positions()
all_pairs = set(list(positions['instrument']))

currs_traded =[]
for currency in to_trade_final['Currency']:
    if currency in all_pairs:
        if positions['volume'][positions['instrument'] == currency].sum() > 2:
            curr_index = to_trade_final[to_trade_final['Currency'] == currency].index.values[0]
            to_trade_final.drop([curr_index], inplace=True)
            currs_traded.append(currency)

if len(currs_traded) > 0:
    telegram_bot_sendtext(str(currs_traded) + ' are ready to trade from screener but have exceeded open positions allowed. FXCM H1')

to_trade_final_limit = pd.read_csv('d:/TradeJournal/tempo_list_h1.csv')
new_comm = [comm+'LMT' for comm in to_trade_final_limit['comment']]
to_trade_final_limit.drop(columns=['comment'],inplace=True)
to_trade_final_limit['comment'] = new_comm
to_trade_final_journal = pd.read_csv('d:/TradeJournal/tempo_list_h1.csv')
to_trade_final_journal = to_trade_final_journal.append(to_trade_final_limit)
to_trade_final_journal.reset_index(inplace=True)
to_trade_final_journal.drop(columns = 'index', inplace=True)
print(to_trade_final_journal)
if len(to_trade_final_journal) == 0:
    telegram_bot_sendtext('No valid setup found. FXCM H1')
else:
    df_journal = pd.read_csv('d:/TradeJournal/trade_journal_h1.csv')
    df_journal = df_journal.append(to_trade_final_journal)
    df_journal.to_csv('d:/TradeJournal/trade_journal_h1.csv', index=False)

for currency in positions['instrument']:
    rsi_close = df_og['rsi'][df_og['Currency'] == currency].values[0]
    pnl = positions['profit'][positions['instrument'] == currency].values[0]
    if positions['position_type'][positions['instrument'] == currency].values[0] == 'sell':
        if rsi_close <= 30:
            MT.Close_position_by_ticket(ticket=positions['ticket'][positions['instrument'] == currency].values[0])
            telegram_bot_sendtext(currency + ' SELL position closed. PNL: ' + str(pnl) + '. RSI value oversold: ' + str(round(rsi_close, 2)))
            time.sleep(1)
    if positions['position_type'][positions['instrument'] == currency].values[0] == 'buy':
        if rsi_close >= 70:
            MT.Close_position_by_ticket(ticket=positions['ticket'][positions['instrument'] == currency].values[0])
            telegram_bot_sendtext(currency + ' BUY position closed. PNL: ' + str(pnl) + '. RSI value bought: ' + str(round(rsi_close, 2)))
            time.sleep(1)   
    else:
      print(currency, ' is okay. ')

open_orders = MT.Get_all_orders()
for item in open_orders['instrument']:
    if item not in set(list(positions['instrument'])):
        MT.Delete_order_by_ticket(ticket=open_orders['ticket'][open_orders['instrument'] == item].values[0])


open_orders = MT.Get_all_orders()
for item in open_orders['instrument']:
    if item not in set(list(positions['instrument'])):
        MT.Delete_order_by_ticket(ticket=open_orders['ticket'][open_orders['instrument'] == item].values[0])

all_orders = list(set(list(positions['instrument'])) | set(list(open_orders['instrument'])))
all_orders_count = []
for currency in all_orders:
    print(currency)
    try:
        open_order = open_orders['volume'][open_orders['instrument'] == currency].sum()
    except:
        open_order = 0
    try:
        open_position = positions['volume'][positions['instrument'] == currency].sum()
    except:
        open_position = 0
    total_currency = open_order + open_position
    all_orders_count.append(total_currency)
all_orders_df = pd.DataFrame(list(zip(all_orders,all_orders_count)), columns=['Currency', 'Total Positions'])

print(to_trade_final_journal)
print(to_trade_final)

for currency in to_trade_final['Currency']:
    total_positions = all_orders_df['Total Positions'][all_orders_df['Currency'] == currency].values[0]
    index_value = all_orders_df['Total Positions'][all_orders_df['Currency'] == currency].index.values[0]
    if total_positions >= 1.0:
        to_trade_final.drop([index_value])

print(to_trade_final_journal)
print(to_trade_final)
#'''
for pair in to_trade_final['Currency']:
    current_price = to_trade_final['Current Price'][to_trade_final['Currency'] == pair].values[0]
    atr_now = to_trade_final['atr'][to_trade_final['Currency'] == pair].values[0]
    dirxn = to_trade_final['Action'][to_trade_final['Currency'] == pair].values[0]
    sloss = round(to_trade_final['sl'][to_trade_final['Currency'] == pair].values[0],5)
    tprof = round(to_trade_final['tp'][to_trade_final['Currency'] == pair].values[0],5)
    spread = MT.Get_last_tick_info(instrument=pair)['spread']
    coms = to_trade_final['comment'][to_trade_final['Currency'] == pair].values[0]
    limit_price = 0
    if dirxn == 'buy':
        limit_price = round((current_price - atr_now),5)
    elif dirxn == 'sell':
        limit_price = round((current_price + atr_now),5)
    vol = round((MT.Get_dynamic_account_info()['balance']*0.000005), 2)*10 #since H1, more trades - half the vol
    if spread <= 130.0:
        order = MT.Open_order(instrument=pair, ordertype=dirxn, volume=vol, openprice = 0.0, slippage = 10, magicnumber=41, stoploss=sloss, takeprofit=tprof, comment =coms)
        order_2 = MT.Open_order(instrument=pair, ordertype=(dirxn+'_limit'), volume=vol, openprice = limit_price, slippage = 10, magicnumber=41, stoploss=sloss, takeprofit=tprof, comment =coms+'LMT')
        if order != -1:    
            telegram_bot_sendtext('FXCM H1 Cerberus setup found. Position opened successfully: ' + pair + ' (' + dirxn.upper() + ') FXCM H1')
            telegram_bot_sendtext('Price: ' + str(current_price) + ', SL: ' + str(sloss) + ', TP: ' + str(tprof))
            time.sleep(3)
        else:
            telegram_bot_sendtext('FXCM H1 Cerberus setup found. ' + (MT.order_return_message).upper() + ' For ' + pair + ' (' + dirxn.upper() + ') FXCM H1')
    else:
        limit_order = MT.Open_order(instrument=pair, ordertype=(dirxn+'_limit'), volume=vol, openprice = limit_price, slippage = 10, magicnumber=41, stoploss=sloss, takeprofit=tprof, comment =coms+'LMT')
        if limit_order != -1:
            telegram_bot_sendtext('FXCM H1 Cerberus setup found but spread too high. ' + pair + ' (' + dirxn.upper() + ' LIMIT), spread: ' + str(spread))
            telegram_bot_sendtext('Price: ' + str(limit_price) + ', SL: ' + str(sloss) + ', TP: ' + str(tprof))
        else:
            telegram_bot_sendtext('FXCM H1 Cerberus setup found but spread too high. ' + (MT.order_return_message).upper() + ' For ' + pair + ' (' + dirxn.upper() + ' LIMIT)')
            telegram_bot_sendtext('Price: ' + str(limit_price) + ', SL: ' + str(sloss)+ ', TP: ' + str(tprof))
telegram_bot_sendtext('Current account equity: USD '+ str(MT.Get_dynamic_account_info()['equity']))
#'''