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
port_dict = {1122:'FTMO', 1125:'FXCM', 1127:'GP', 1129:'GP Demo'}
master = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCAD','GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'NZDCHF','USDCAD', 'USDCHF', 'USDJPY']


list_symbols_jpy = ['AUDJPY','CADJPY', 'EURJPY','CHFJPY', 'GBPJPY', 'NZDJPY', 'USDJPY']
# list_symbols_usd = ['AUDUSD','USDCAD', 'EURUSD','USDCHF', 'GBPUSD', 'NZDUSD']

list_df = ['AUD','CAD', 'EUR','CHF', 'GBP', 'NZD', 'USD']
symbols = {}
for pair in master:
    symbols[pair] = pair

con = MT.Connect(server='127.0.0.1', port=1129, instrument_lookup=symbols)

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
    prev_price_l = []
    current_price_l = []
    sma_l = []
    sma_prev_l = []
    for currency in list_symbols_jpy:
        print(currency)
        bars = pd.DataFrame(MT.Get_last_x_bars_from_now(instrument = currency, timeframe = MT.get_timeframe_value(tf), nbrofbars=1800))
        print(bars)
        prev_price = bars['close'].loc[len(bars) - 2]
        prev_price_l.append(prev_price)
        current_price = bars['close'].loc[len(bars) - 1]
        current_price_l.append(current_price)
        sma_raw = ta.sma(close = bars['close'], length=200, append=True)
        bars['sma200'] = sma_raw
        sma_prev = sma_raw[len(bars)-3]
        sma_prev_l.append(sma_prev)
        sma = sma_raw[len(bars)-2]
        sma_l.append(sma)
    df_raw['price'] = current_price_l
    df_raw['sma200'] = sma_l
    df_raw['prev_price'] = prev_price_l
    df_raw['prev_sma200'] = sma_prev_l
    df_raw['swab'] = (np.array(df_raw['price']) - np.array(df_raw['sma200']))/(np.array(df_raw['sma200']))*100
    df_raw['swab prev'] = (np.array(df_raw['prev_price']) - np.array(df_raw['prev_sma200']))/(np.array(df_raw['prev_sma200']))*100
    print(list(df_raw.head()))
    df_raw.loc[len(df_raw)] = ['JPY', 0, 0, 0, 0, 0, 0]
    df_raw.sort_values(by='swab', ascending = False, inplace=True)
    df_raw.reset_index(inplace=True)
    df_raw.drop(columns=['index'], inplace=True)
    return df_raw

def pair_score(pair):
    first = pair[0:3]
    second = pair[3:]
    first_score = df['swab'][df['Currency'] == first].values[0]
    second_score = df['swab'][df['Currency'] == second].values[0]
    return first_score - second_score

def pair_score_prev(pair):
    first = pair[0:3]
    second = pair[3:]
    first_score = df['swab prev'][df['Currency'] == first].values[0]
    second_score = df['swab prev'][df['Currency'] == second].values[0]
    return first_score - second_score

def dirxn(pair):
    if pair < 0:
        return 'sell'
    elif pair > 0:
        return 'buy'
    else:
        return 'na'


df = swab_test(tf='H4')
to_trade_raw = pd.DataFrame()
to_trade_raw['Currency'] = master
to_trade_raw['swab_score'] = [pair_score(pair) for pair in master]
to_trade_raw['swab_score_prev'] = [pair_score_prev(pair) for pair in master]
to_trade_raw['dirxn'] = [dirxn(pair) for pair in to_trade_raw['swab_score']]
to_trade_raw['swab_abs'] = to_trade_raw['swab_score'].map(lambda x:abs(x))
to_trade_raw['swab_abs_prev'] = to_trade_raw['swab_score_prev'].map(lambda x:abs(x))
to_trade_raw.sort_values(by='swab_abs', ascending = False, inplace=True)
to_trade_raw.reset_index(inplace=True)
to_trade_raw.drop(columns=['index'], inplace=True)

print(to_trade_raw)
to_trade_final = to_trade_raw[(to_trade_raw['swab_abs'] >= 2.0) & (to_trade_raw['swab_abs_prev'] < 2.0)]
print(to_trade_final)
msg_trade_final = []
for currency in to_trade_final['Currency']:
    buy_or_sell = (to_trade_final['dirxn'][to_trade_final['Currency'] == currency].values[0]).upper()
    score = str(round((to_trade_final['swab_abs'][to_trade_final['Currency'] == currency].values[0]),2))
    msg_trade_final.append(buy_or_sell + ' '+ currency + ' (' + score + ')')

text = []
for currency in df['Currency']:
    text.append(currency + ': ' + str(round(df['swab'][df['Currency'] == currency].values[0], 2))+'%')

message = " || ".join(text)
telegram_bot_sendtext('SWAB\n\n'+message)

if len(to_trade_final) == 0:
    telegram_bot_sendtext("No trade setup found.")
    exit()
else:
    message_2 = " || ".join(msg_trade_final)
    telegram_bot_sendtext(message_2)

print(to_trade_final)

signal = to_trade_final['Currency'].unique() #there should be a position
print(signal)
#count open positions, if greater than 2 ignore - - no need, if positive

#move open positions with 2.8 above to BE
positions = MT.Get_all_open_positions()
current = positions['instrument'].unique()

for item in current:
    tix = positions['ticket'][positions['instrument'] == item].values[0]
    score = round(to_trade_raw['swab_abs'][to_trade_raw['Currency'] == item].values[0],2)
    if item not in signal:
        if score < 1.8:
            MT.Close_position_by_ticket(ticket=tix)
            telegram_bot_sendtext('SWAB: Closing position for ' + item + ' (' + str(score) +')')
    elif score > 3.0:
        MT.Close_position_by_ticket(ticket=tix)
        telegram_bot_sendtext('SWAB: Closing position for ' + item, + '. Reached 3% threshold.')

for item in signal:
    if item not in current:
        vol = 0.01
        dirxn = to_trade_final['dirxn'][to_trade_final['Currency'] == item].values[0]
        order = MT.Open_order(instrument=item, ordertype=(dirxn), volume=vol, openprice = 0, slippage = 10, magicnumber=42, stoploss=0, takeprofit=0, comment ='SWAB_v2b18b2')
        if order != -1:    
            telegram_bot_sendtext('SWB setup found. Position opened successfully: ' + item + ' (' + dirxn.upper() + ')')
            time.sleep(1)
        else:
            telegram_bot_sendtext('SWB setup found. ' + (MT.order_return_message).upper() + ' For ' + item + ' (' + dirxn.upper() + ')')

#trailstop idea - create a prev score. if current score lower than prev score by x%(eg 0.2%), close
#only open new trades if prev score lower than 2 - this prevents opening new trades after closing from trailstop