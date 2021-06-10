import datetime
from datetime import datetime
from pathlib import Path
from termcolor import colored, cprint
import time
import asyncio
import os
import requests
from check_news import *
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCAD','GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair
port = 1122 #FTMO
con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup=symbols)

home = str(Path.home())
t_gram_creds = open((home+'/Desktop/t_gram.txt'), 'r')
bot_token = t_gram_creds.readline().split('\n')[0]
bot_chatID = t_gram_creds.readline()
t_gram_creds.close()

df_pairs = pd.read_csv(home+'/Desktop/Experimental/v4/macdema_test.csv')

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

def basket_close(target=500, lot_based='no', per_lot = 1, port=0):
    positions = MT.Get_all_open_positions()
    pnl = positions['profit'].sum()
    if lot_based == 'no':
        if pnl >= target:
            for ticket in positions['ticket']:
                MT.Close_position_by_ticket(ticket=ticket)
                telegram_bot_sendtext('All positions closed. Basket target reached. Profit: ' + str(round(pnl, 2)))
        # else:
        #     print('Target profit not reached. Current PNL: ' + str(pnl))
    elif lot_based == 'yes':
        total_lot = positions['volume'].sum()
        target_x = total_lot*per_lot
        if pnl >= target_x:
            for ticket in positions['ticket']:
                MT.Close_position_by_ticket(ticket=ticket)
                telegram_bot_sendtext('All positions closed. Basket target reached. Profit: ' + str(round(pnl, 2)))
        # else:
        #     print('Target profit not reached. Current PNL: ' + str(pnl))

def break_even(pair, atr_target = 4, amount = 0.2, port=0):
    positions = MT.Get_all_open_positions()
    dirxn = positions['position_type'][positions['instrument'] == pair].values[0]
    atr = df_pairs['atr'][df_pairs['Currency'] == pair].values[0]
    if dirxn == 'buy':
        current_price = MT.Get_last_tick_info(instrument=pair)['bid']
        if current_price >= (positions['open_price'][positions['instrument'] == pair].values[0])+(atr_target*atr):
            be_sl = (positions['open_price'][positions['instrument'] == pair].values[0]) + (positions['open_price'][positions['instrument'] == pair].values[0])+(amount*atr)
            try:
                MT.Set_sl_and_tp_for_position(ticket=(positions['ticket'][positions['instrument']==pair].values[0]), stoploss=be_sl, takeprofit=0)
                telegram_bot_sendtext(pair + ' (' + dirxn.upper() + ') hit 2ATR. Successfully moved SL to BE.')
            except:
                error = MT.order_return_message
                telegram_bot_sendtext(error)
        # else:
        #     print(pair + ' not yet reaching ' + str(atr_target) + ' ATR')
    if dirxn == 'sell':
        current_price = MT.Get_last_tick_info(instrument=pair)['bid']
        if current_price <= (positions['open_price'][positions['instrument'] == pair].values[0])-(atr_target*atr):
            be_sl = (positions['open_price'][positions['instrument'] == pair].values[0]) - (positions['open_price'][positions['instrument'] == pair].values[0])+(amount*atr)
            try:
                MT.Set_sl_and_tp_for_position(ticket=(positions['ticket'][positions['instrument']==pair].values[0]), stoploss=be_sl, takeprofit=0)
                telegram_bot_sendtext(pair + ' (' + dirxn.upper() + ') hit 2ATR. Successfully moved SL to BE.')
            except:
                error = MT.order_return_message
                telegram_bot_sendtext(error)
        # else:
        #     print(pair + ' not yet reaching ' + str(atr_target) + ' ATR')
print("Tanod is running....")
higher_pnl = 0
heartbeat_list = [0,5,10,15,20, 25,30,35,40,45,50,55]
while datetime.now().weekday() <= 4:
    positions = MT.Get_all_open_positions()
    pnl = positions['profit'].sum()
    if len(positions) > 0:
        basket_close(target=500, lot_based='no', per_lot = 1)
        time.sleep(1)
        for currency in positions['instrument']:
            break_even(pair = currency, atr_target = 6, amount = 0.3)
            time.sleep(1)
            check_news(pair)
            if pnl > higher_pnl:
                higher_pnl = pnl
                print(datetime.now().strftime('%H:%M') + " - Tanod is watching " + str(len(positions)) + " trade/s. Current PNL: " + str(round(positions['profit'].sum(), 2)))
    else:
        timestmp = datetime.now().strftime('%H:%M')
        print(timestmp + ' - No positions monitored.')
        time.sleep(60)
