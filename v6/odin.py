'''
Strat

- Run on wed open candle
- Check prev wk slow+fast rsi bias
- Check mon+tue rsi bias 
- if wk bias == montue bias, action bias
- stop = 3ATR (H4)
- exit = 5ATR (H4), 
    - to implement exit - if wk bias change on next week, close
    - able to stack if same bias

to do:
- add prev week rsi, if not 2 weeks on same bias, ignore
- add close all if entries are left still

Update to include GP Live

'''

import pandas as pd
from pytz import timezone
import pytz
import requests
import datetime
from datetime import date, datetime, timedelta, tzinfo
import time
from pathlib import Path
import pandas_ta as ta
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
ports = [1122, 1125, 1127, 1129, 1131]
port_dict = {1122:'FTMO_Live', 1125:'FXCM_Demo', 1127:'GP_Live', 1129:'GP_Demo', 1131:'FTMO_Demo'}

if datetime.now().weekday() > 4: #don't run on weekends
    exit()
else:
    pass

# list_symbols = ['AUDCAD','AUDUSD','EURUSD', 'GBPUSD','NZDUSD','USDCAD','USDCHF','USDJPY'] #2021 best performing
list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCAD','GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair

con = MT.Connect(server='127.0.0.1', port=1131, instrument_lookup=symbols)

home = str(Path.home())
t_gram_creds = open((home+'/Desktop/t_gram.txt'), 'r')
bot_token = t_gram_creds.readline().split('\n')[0]
bot_chatID = t_gram_creds.readline()
t_gram_creds.close()
timezone = pytz.timezone("Etc/UTC")
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

def reverse(og):
    if og == 'buy':
        return 'sell'
    elif og == 'sell':
        return 'buy'

def trade_odin(port, vol, rev=False):
    con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup=symbols)
    if con == True:
        for currency in to_trade_final_raw['Currency']:
            dirxn = ""
            if rev == False:
                dirxn = to_trade_final_raw['Action'][to_trade_final_raw['Currency'] == currency].values[0]
            else:
                dirxn = reverse(to_trade_final_raw['Action'][to_trade_final_raw['Currency'] == currency].values[0])
            sloss = to_trade_final_raw['sl'][to_trade_final_raw['Currency'] == currency].values[0]
            tprof = to_trade_final_raw['tp'][to_trade_final_raw['Currency'] == currency].values[0]
            coms = 'ODN_v2_'+port_dict[port]
            order = MT.Open_order(instrument=currency, ordertype=dirxn, volume=vol, openprice = 0.0, slippage = 10, magicnumber=port, stoploss=0, takeprofit=0, comment =coms)
            time.sleep(1)
            print(currency, order)
            if order == -1:
                telegram_bot_sendtext('ODIN - ERROR opening order for '+ currency + '-'+ dirxn.upper())
    else:
        telegram_bot_sendtext('Odin failed for '+port_dict[port] + '.')


all_curr = pd.DataFrame(columns=['Currency', 'mon_open', 'wed_open', 'rsi', 'rsi wk 14', 'rsi wk 100', 'rsi wk bias'])

# open_positions = MT.Get_all_open_positions()
# print(len(open_positions))
# profit = open_positions['profit'].sum()
# if len(open_positions) > 0:
#     telegram_bot_sendtext('Closing open positions. PNL:$' + str(profit))
#     for ticket in open_positions['ticket']:
#         close_order = MT.Close_position_by_ticket(ticket=ticket)

for currency in list_symbols:
    print(currency)
    bars = pd.DataFrame(MT.Get_last_x_bars_from_now(instrument = currency, timeframe = MT.get_timeframe_value('D1'), nbrofbars=300))
    bars_wk = pd.DataFrame(MT.Get_last_x_bars_from_now(instrument = currency, timeframe = MT.get_timeframe_value('W1'), nbrofbars=300))
    rsi_trend_raw = ta.rsi(bars['close'], length = 100)
    rsi_trend_wk_slow_raw = ta.rsi(bars_wk['close'], length = 100)
    rsi_trend_wk_fast_raw = ta.rsi(bars_wk['close'], length = 14)
    bars['rsi trend'] = rsi_trend_raw
    bars['rsi wk 14'] = rsi_trend_wk_fast_raw
    bars['rsi wk 100'] = rsi_trend_wk_slow_raw
    to_all_curr = []
    to_all_curr.append(currency)
    mon_open = bars['open'].loc[len(bars)-3] #3
    to_all_curr.append(mon_open)
    wed_open = bars['open'].loc[len(bars)-1] #1
    to_all_curr.append(wed_open)
    mon_rsi_raw = bars['rsi trend'].loc[len(bars)-3] #3
    tues_rsi_raw = bars['rsi trend'].loc[len(bars)-2] #2
    if tues_rsi_raw > 50 and mon_rsi_raw > 50:
        to_all_curr.append('buy')
    elif tues_rsi_raw < 50 and mon_rsi_raw < 50:
        to_all_curr.append('sell')
    else:
        to_all_curr.append('ignore')
    wk_fast_rsi = bars['rsi wk 14'].loc[len(bars)-2]
    to_all_curr.append(wk_fast_rsi)
    wk_slow_rsi = bars['rsi wk 100'].loc[len(bars)-2]
    to_all_curr.append(wk_slow_rsi)
    if wk_fast_rsi > 50 and wk_slow_rsi > 50:
        to_all_curr.append('buy')
    elif wk_fast_rsi < 50 and wk_slow_rsi < 50:
        to_all_curr.append('sell')
    else:
        to_all_curr.append('ignore')
    all_curr.loc[len(all_curr)] = to_all_curr

action = []

action_raw = []
for line in range(0, len(all_curr)):
    if (all_curr['mon_open'].loc[line] > all_curr['wed_open'].loc[line]) and all_curr['rsi'].loc[line] == 'sell' and all_curr['rsi wk bias'].loc[line] == 'sell': #og = all_curr['rsi trend'].loc[line] == 'sell'
        action_raw.append('buy')
    elif (all_curr['mon_open'].loc[line] < all_curr['wed_open'].loc[line]) and all_curr['rsi'].loc[line] == 'buy' and all_curr['rsi wk bias'].loc[line] == 'buy':  #og = all_curr['rsi trend'].loc[line] == 'buy'
        action_raw.append('sell')
    else:
        action_raw.append('ignore')
all_curr['Action'] = action_raw

to_trade_final_raw = all_curr[all_curr['Action'] != 'ignore']
to_trade_final_raw.reset_index(inplace = True)
to_trade_final_raw.drop(columns = 'index', inplace = True)

exits = pd.read_csv('d:/TradeJournal/cerberus_raw_FTMO.csv')

sls = []
tps = []
for currency in to_trade_final_raw['Currency']:
    current_price = MT.Get_last_tick_info(instrument=currency)['bid']
    if to_trade_final_raw['Action'][to_trade_final_raw['Currency'] == currency].values[0] == 'buy':
        sls.append(current_price - (exits['atr'][exits['Currency'] == currency].values[0])*3.3)        
        tps.append(current_price + (exits['atr'][exits['Currency'] == currency].values[0])*5)
    elif to_trade_final_raw['Action'][to_trade_final_raw['Currency'] == currency].values[0] == 'sell':
        sls.append(current_price + (exits['atr'][exits['Currency'] == currency].values[0])*3.3)        
        tps.append(current_price - (exits['atr'][exits['Currency'] == currency].values[0])*5)
    else:
        sls.append(0)
        tps.append(0)
to_trade_final_raw['sl'] = sls
to_trade_final_raw['tp'] = tps

print(to_trade_final_raw)

ftmo_vol = 0
gp_live_vol = 0
gp_demo_vol = 0
fxcm_demo = 0

if len(to_trade_final_raw) < 4:
    ftmo_vol = 3
    gp_live_vol = 0.03
    gp_demo_vol = 0.5
    fxcm_demo = 3
else:
    ftmo_vol = round((12/len(to_trade_final_raw)),2)
    gp_live_vol = round((0.15/len(to_trade_final_raw)),2)
    gp_demo_vol = round((2/len(to_trade_final_raw)),2)
    fxcm_demo = round((12/len(to_trade_final_raw)),2)
# port_dict = {1122:'FTMO_Live', 1125:'FXCM_Demo', 1127:'GP_Live', 1129:'GP_Demo', 1131:'FTMO_Demo'}

if datetime.now().hour >= 19:
    con = MT.Connect(server='127.0.0.1', port=1125, instrument_lookup=symbols)
    morning = MT.Get_closed_positions_within_window(date_from=datetime(date.today().year,date.today().month,date.today().day, tzinfo=timezone), date_to=datetime.now())['profit'].sum()
    if morning < 0:
        telegram_bot_sendtext('Odin defeated in the morning. Reverse.')
        trade_odin(port = 1122, vol = ftmo_vol, rev=True)
        # trade_odin(port = 1125, vol = fxcm_demo, rev=True)
        # trade_odin(port = 1127, vol= gp_live_vol,rev=True)
        # trade_odin(port=1129, vol=gp_demo_vol, rev=True)
        trade_odin(port=1131, vol=ftmo_vol, rev=True)
    elif morning > 0:
        telegram_bot_sendtext('Odin is triumphant this morning. We charge!')
        trade_odin(port = 1122, vol = ftmo_vol)
        # trade_odin(port = 1125, vol = fxcm_demo)
        # trade_odin(port = 1127, vol= gp_live_vol)
        # trade_odin(port=1129, vol=gp_demo_vol)
        trade_odin(port=1131, vol=ftmo_vol)
elif datetime.now().hour == 7:
        telegram_bot_sendtext('Odin will now test the waters.')
        # trade_odin(port = 1122, vol = ftmo_vol)
        trade_odin(port = 1125, vol = fxcm_demo)
        # trade_odin(port = 1127, vol= gp_live_vol)
        # trade_odin(port=1129, vol=gp_demo_vol)
        # trade_odin(port=1131, vol=ftmo_vol)