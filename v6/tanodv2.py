import datetime
from datetime import datetime
from pathlib import Path
from termcolor import colored, cprint
import time
import os
import requests
from Pytrader_API_V1_06 import *
MT = Pytrader_API()

if datetime.now().weekday() > 5: #don't run on weekends
    exit()
elif datetime.now().weekday() == 5 and datetime.now().hour > 5: #last saturday 5am
    exit()
elif datetime.now().weekday() == 0 and datetime.now().hour < 5: #monday before 5am
    exit()
else:
    pass

list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCAD','GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair
port = 1131 #FTMO
con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup=symbols)

home = str(Path.home())
t_gram_creds = open((home+'/Desktop/t_gram_swab1hr.txt'), 'r')
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

def basket_close(target=500, lot_based='no', per_lot = 1, shirt_protect = 'yes', shirt_protect_amt = 2000, port=0):
    positions = MT.Get_all_open_positions()
    pnl = positions['profit'].sum()
    if lot_based == 'no':
        if pnl >= target:
            for ticket in positions['ticket']:
                MT.Close_position_by_ticket(ticket=ticket)
            telegram_bot_sendtext('All positions closed. Basket target reached. Profit: ' + str(round(pnl, 2)))
    elif lot_based == 'yes':
        total_lot = positions['volume'].sum()
        target_x = total_lot*per_lot
        if pnl >= target_x:
            for ticket in positions['ticket']:
                MT.Close_position_by_ticket(ticket=ticket)
            telegram_bot_sendtext('All positions closed. Basket target reached. Profit: ' + str(round(pnl, 2)))
    else:
        pass
    
    if shirt_protect == 'yes':
        if pnl >= shirt_protect_amt:
            for ticket in positions['ticket']:
                MT.Close_position_by_ticket(ticket=ticket)
            telegram_bot_sendtext('All positions closed. Shirt protect activated. Loss: ' + str(round(pnl, 2)))

heartbeat_list = [0,5,10,15,20, 25,30,35,40,45,50,55]
prev_pnl = 0
print('\nTanod on duty.\n')
while datetime.now().minute < 60:
    if datetime.now().minute == 0:
        print('Restarting.')
        exit()

    positions = MT.Get_all_open_positions()
    pnl = positions['profit'].sum()
    total_positions = positions['volume'].sum()
    if total_positions == 0:
        print(f'No positions as of {datetime.now().strftime("%H:%M:%S")}.', end='\r')
    
    else:
        if datetime.now().minute in heartbeat_list:
            if pnl != prev_pnl:
                print(f'Current {round(pnl,2)}, Target: {round(total_positions*1000,2)}', end='\r')
                pnl = prev_pnl
        
        if len(positions) > 0:
            basket_close(target=round(1000*total_positions,2), lot_based='no', per_lot = 300, shirt_protect='yes', shirt_protect_amt=round(-1000*total_positions,2))
            time.sleep(1)
    
