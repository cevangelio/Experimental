##SWAB
'''

200 SMA H4

distance from price

vs JPY

MA-price/price


ranking

rank 1+rank 8 trade this

filter 2% differential rule (can be 1.5 to 2%), extreme (record high or record low)

if top 1 is 1%
top8 -1.5%
add = 2.5%

no trade news

70-75%

5 max ope positions

1%, 1.5% SL

no trade after 5%

1% per trade

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
ports = [1127]
port_dict = {1122:'FTMO', 1125:'FXCM', 1127:'GP'}
master = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCAD','GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'NZDCHF','USDCAD', 'USDCHF', 'USDJPY']


# list_symbols_jpy = ['AUDJPY','CADJPY', 'EURJPY','CHFJPY', 'GBPJPY', 'NZDJPY', 'USDJPY']
list_symbols_usd = ['AUDUSD','USDCAD', 'EURUSD','USDCHF', 'GBPUSD', 'NZDUSD', 'USDJPY']

list_df = ['AUD','CAD', 'EUR','CHF', 'GBP', 'NZD', 'JPY']
symbols = {}
for pair in master:
    symbols[pair] = pair

con = MT.Connect(server='127.0.0.1', port=ports[0], instrument_lookup=symbols)

home = str(Path.home())
t_gram_creds = open((home+'/Desktop/t_gram.txt'), 'r')
bot_token = t_gram_creds.readline().split('\n')[0]
bot_chatID = t_gram_creds.readline()
t_gram_creds.close()

if datetime.now().weekday() > 5: #don't run on weekends
    exit()
elif datetime.now().weekday() == 5 and datetime.now().hour > 5: #last saturday 5am
    exit()
elif datetime.now().weekday() == 0 and datetime.now().hour < 5: #monday before 5am
    exit()
else:
    pass

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

def swab_test(tf='H4'):
    df_raw = pd.DataFrame()
    df_raw['Currency'] = list_df
    current_price_l = []
    sma_l = []
    for currency in list_symbols_usd:
        print(currency)
        bars = pd.DataFrame(MT.Get_last_x_bars_from_now(instrument = currency, timeframe = MT.get_timeframe_value(tf), nbrofbars=600))
        print(bars)
        current_price = bars['close'].loc[len(bars) - 1]
        current_price_l.append(current_price)
        sma_raw = ta.sma(close = bars['close'], length=200, append=True)
        bars['sma200'] = sma_raw
        sma = sma_raw[len(bars)-2]
        sma_l.append(sma)
    df_raw['price'] = current_price_l
    df_raw['sma200'] = sma_l
    return df_raw

def check_pair(top, bottom):
    if top + bottom in master:
        return top+bottom
    else:
        return bottom + top

def pair_score(pair):
    first = pair[0:3]
    second = pair[3:]
    first_score = df['swab'][df['Currency'] == first].values[0]
    try:
        second_score = df['swab'][df['Currency'] == second].values[0]
    except:
        second_score = 0
    return first_score - second_score

def dirxn(pair):
    first = pair[0:3]
    second = pair[3:]
    first_score = df['swab_abs'][df['Currency'] == first].values[0]
    second_score = df['swab_abs'][df['Currency'] == second].values[0]
    dominant = ""
    if first_score > second_score:
        dominant = first
    else:
        dominant = second
    raw_score_dominant = df['swab'][df['Currency'] == dominant].values[0]
    if raw_score_dominant > 0 and dominant == first:
        return 'buy'
    elif raw_score_dominant < 0 and dominant == first:
        return 'sell'
    elif raw_score_dominant > 0 and dominant == second:
        return 'sell'
    elif raw_score_dominant < 0 and dominant == second:
        return 'buy'


df = swab_test(tf='H4')

action = []
for line in range(0, len(df)):
    if df['price'].loc[line] > df['sma200'].loc[line]:
        action.append('buy')
    else:
        action.append('sell')
df['swab'] = (np.array(df['price']) - np.array(df['sma200']))/(np.array(df['sma200']))*100
df.sort_values(by='swab', ascending = False, inplace=True)
df.reset_index(inplace=True)
df.drop(columns=['index'], inplace=True)
df['swab_abs'] = df['swab'].map(lambda x:abs(x))
#pair strongest to weakest, check value, if above 1.2 then take action

print(df)

strongest = df['Currency'].loc[0]
weakest_1 = df['Currency'].loc[len(df)-1]
weakest_2 = df['Currency'].loc[len(df)-2]
top_1_score = df['swab_abs'].loc[0]

#determine right pairing name
#determine direction

to_trade = pd.DataFrame()
to_trade_curr = []
top_1 = strongest+weakest_1
top_2 = strongest+weakest_2
to_trade_curr.append(check_pair(strongest, weakest_1))
to_trade_curr.append(check_pair(strongest, weakest_2))
to_trade['Currency'] = to_trade_curr
to_trade['score'] = [pair_score(pair) for pair in to_trade_curr]
to_trade_action = []
for score in to_trade['score']:
    if 1.5 <= score <= 2.5:
        to_trade_action.append('trade')
    else:
        to_trade_action.append('ignore')
to_trade['action'] = to_trade_action
to_trade['dirxn'] = [dirxn(pair) for pair in to_trade_curr]
to_trade['current price'] = [MT.Get_last_tick_info(instrument=currency)['bid'] for currency in to_trade['Currency']]
print(to_trade)
exits = pd.read_csv('d:/TradeJournal/cerberus_raw_FTMO.csv')

to_trade_final = to_trade[to_trade['action']!='ignore']
if len(to_trade_final) == 0:
    telegram_bot_sendtext("No trade setup found.")
    exit()
else:
    pass

sls = []
tps = []
open_price = []
for currency in to_trade_final['Currency']:
    current_price = MT.Get_last_tick_info(instrument=currency)['bid']
    if to_trade_final['dirxn'][to_trade_final['Currency'] == currency].values[0] == 'buy':
        open_price.append(current_price - (exits['atr'][exits['Currency'] == currency].values[0])*0.5)
        sls.append(current_price - (exits['atr'][exits['Currency'] == currency].values[0])*3.3)        
        tps.append(current_price + (exits['atr'][exits['Currency'] == currency].values[0])*8.8)
    elif to_trade['dirxn'][to_trade['Currency'] == currency].values[0] == 'sell':
        open_price.append(current_price + (exits['atr'][exits['Currency'] == currency].values[0])*0.5)
        sls.append(current_price + (exits['atr'][exits['Currency'] == currency].values[0])*3.3)        
        tps.append(current_price - (exits['atr'][exits['Currency'] == currency].values[0])*8.8)
    else:
        sls.append(0)
        tps.append(0)
to_trade_final['limit price'] = open_price
to_trade_final['sl'] = sls
to_trade_final['tp'] = tps

text = []
for currency in df['Currency']:
    text.append(currency + ': ' + str(round(df['swab'][df['Currency'] == currency].values[0], 2))+'%')

message = " || ".join(text)
telegram_bot_sendtext('SWAB\n\n'+message)

print(to_trade_final)

#count open positions, if greater than 2 ignore - - no need, if positive

#move open positions with 2.8 above to BE

positions = MT.Get_all_open_positions()
pend_positions = MT.Get_all_orders()
all_pairs = set(list(positions['instrument']) + list(pend_positions['instrument']))
print(all_pairs)
for currency in all_pairs:
    pip = (MT.Get_instrument_info(instrument = currency)['point'])*10
    print(currency)
    swab_score = pair_score(currency)
    print(currency, swab_score)
    if swab_score >= 3.0:
        to_close = positions[positions['instrument'] == currency]
        for tix in to_close['ticket']:
            magic_num = positions['magic_number'][positions['ticket']==tix].values[0]
            if magic_num == 42:
                move = ""
                if positions['position_type'][positions['ticket']==tix].values[0] == 'sell':
                    new_sl = positions['open_price'][positions['ticket'] == tix] - 3*pip
                    move = MT.Set_sl_and_tp_for_order(ticket=tix, stoploss=new_sl, takeprofit=0)
                elif positions['position_type'][positions['ticket']==tix].values[0] == 'buy':
                    new_sl = positions['open_price'][positions['ticket'] == tix] + 3*pip
                    move = MT.Set_sl_and_tp_for_order(ticket=tix, stoploss=new_sl, takeprofit=0)
                if move == True:
                    telegram_bot_sendtext(currency + ' position moved to BE (ticket' + str(tix) + '). SWB score: '+str(swab_score))
                else:
                    telegram_bot_sendtext(currency + ' position move to BE <FAILED> (ticket' + str(tix) + '). SWB score: '+str(swab_score))

broker = port_dict[ports[0]]
for pair in to_trade_final['Currency']:
    currs_traded = []
    if pair in all_pairs:
        if len(positions[positions['instrument'] == pair])  >= 1 or len(pend_positions[pend_positions['instrument'] == pair]) >=1:
            curr_index = to_trade_final[to_trade_final['Currency'] == pair].index.values[0]
            to_trade_final.drop([curr_index], inplace=True)
            currs_traded.append(currency)
    if len(currs_traded) > 0:
        telegram_bot_sendtext(broker + ': ' + str(currs_traded) + ' are ready to trade from screener but have exceeded open positions allowed.')

#trade, limit orders only (0.5 ATR from current price)
'''
for pair in to_trade_final['Currency']:
    vol = 0.01
    dirxn = to_trade_final['dirxn'][to_trade_final['Currency'] == pair].values[0]
    limit_price = to_trade_final['limit price'][to_trade_final['Currency'] == pair].values[0]
    sloss = to_trade_final['sl'][to_trade_final['Currency'] == pair].values[0]
    tprof = to_trade_final['tp'][to_trade_final['Currency'] == pair].values[0]
    broker = port_dict[ports[0]]
    order = MT.Open_order(instrument=pair, ordertype=(dirxn+'_limit'), volume=vol, openprice = limit_price, slippage = 10, magicnumber=42, stoploss=sloss, takeprofit=tprof, comment ='SWAB_v1')
    if order != -1:    
        telegram_bot_sendtext(broker + ': ' + 'SWB setup found. Limit position opened successfully: ' + pair + ' (' + dirxn.upper() + ')')
        telegram_bot_sendtext('Price: ' + str(limit_price) + ', SL: ' + str(sloss) + ', TP: ' + str(tprof))
        time.sleep(3)
    else:
        telegram_bot_sendtext(broker + ': ' + 'SWB setup found. ' + (MT.order_return_message).upper() + ' For ' + pair + ' (' + dirxn.upper() + ')')
'''
