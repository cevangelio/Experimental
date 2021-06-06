import asyncio
import datetime
from datetime import datetime
from pathlib import Path
import time
import os
import requests
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
port = 1125 #FXCM MAIN 50k 1:100
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

def basket_close(target=500, lot_based='no', per_lot = 1,shirt_protect='yes', s_p=0.05):
    positions = MT.Get_all_open_positions()
    pnl = positions['profit'].sum()
    balance = MT.Get_dynamic_account_info()['balance']
    if lot_based == 'no':
        if pnl >= target:
            for ticket in positions['ticket']:
                MT.Close_position_by_ticket(ticket=ticket)
                telegram_bot_sendtext('All positions closed. Basket target reached. Profit: ' + str(round(pnl, 2)))
        elif shirt_protect == 'yes' and pnl <= (-balance*s_p):
            for ticket in positions['ticket']:
                MT.Close_position_by_ticket(ticket=ticket)
                telegram_bot_sendtext('All positions closed. Shirt protection activated. Profit: ' + str(round(pnl, 2)))
    elif lot_based == 'yes':
        total_lot = positions['volume'].sum()
        target_x = total_lot*per_lot
        if pnl >= target_x:
            for ticket in positions['ticket']:
                MT.Close_position_by_ticket(ticket=ticket)
                telegram_bot_sendtext('All positions closed. Basket target reached. Profit: ' + str(round(pnl, 2)))


home = str(Path.home())
profit_factor = 0.01
while datetime.now().weekday() <= 5:
    positions = MT.Get_all_open_positions()
    total_positions = positions['volume'].sum()
    float_pnl = positions['profit'].sum()
    timestmp = datetime.now().strftime('%H:%M')
    balance = MT.Get_dynamic_account_info()['balance']
    profit_factor = 0.01
    if total_positions == 0:
        print('Zero positions left. Cerberus unleashed.')
        x = os.popen('python3 ' +home +'/Desktop/Experimental/v4/cerberus.py').read()
        time.sleep(60)
        print('Basket opened.')
    else:
        basket_close(target=(round(balance*profit_factor,0)))
        prev = datetime.now().minute
        time.sleep(1)
        new = datetime.now().minute
        if new > prev:
            print(timestmp + ' - Positions still open. Checking in 60 seconds. Current PNL: ' + str(round(float_pnl, 2)))
