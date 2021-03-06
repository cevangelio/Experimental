#stacker

import pandas as pd
import requests
from datetime import date, datetime
import time
from pathlib import Path
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
ports = [1122,1125,1127]
port_dict = {1122:'FTMO', 1125:'FXCM', 1127:'GP'}

list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCAD','GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'NZDCHF', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair
strat = {41:'CBR', 42:'SWB', 43:'ODN', 0:'MNX'}

home = str(Path.home())
t_gram_creds = open((home+'/Desktop/t_gram.txt'), 'r')
bot_token = t_gram_creds.readline().split('\n')[0]
bot_chatID = t_gram_creds.readline()
t_gram_creds.close()

def telegram_bot_sendtext(bot_message):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

currency_data = pd.read_csv('d:/TradeJournal/cerberus_raw_GP.csv')

def stack(port):
    con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup=symbols)
    try:
        open_positions = MT.Get_all_open_positions()
    except:
        open_positions = pd.DataFrame()
    open_orders = MT.Get_all_orders()
    if len(open_positions) > 0:
        for ticket in open_positions['ticket']:
            currency = open_positions['instrument'][open_positions['ticket'] == ticket].values[0]
            current_sl = open_positions['stop_loss'][open_positions['ticket'] == ticket].values[0]
            print(currency)
            currency_open_positions = len(open_positions[open_positions['instrument']==currency]) + len(open_orders[(open_orders['instrument'] == currency) & (open_orders['comment'] == 'stack_v1')])
            atr = currency_data['atr'][currency_data['Currency'] == currency].values[0]
            current_price = MT.Get_last_tick_info(instrument=currency)['bid']
            open_price = open_positions['open_price'][open_positions['ticket'] == ticket].values[0]
            dirxn = open_positions['position_type'][open_positions['ticket'] == ticket].values[0]
            magic_num = open_positions['magic_number'][open_positions['ticket'] == ticket].values[0]
            vol = open_positions['volume'][open_positions['ticket'] == ticket].values[0]
            if dirxn == 'sell':
                limit_price = current_price + (0.5*atr)
                distance = open_price - current_price
                new_sl = limit_price + (1.5*atr)
                if distance >= 2*atr:
                    max_positions = distance//(2*atr) + 1
                    if currency_open_positions < max_positions:
                        order = MT.Open_order(instrument=currency, ordertype=(dirxn+'_limit'), volume=vol, openprice = limit_price, slippage = 10, magicnumber=magic_num, stoploss=new_sl, takeprofit=0, comment ='stack_v1')
                        if order != -1:    
                            telegram_bot_sendtext(port_dict[port]+'-'+strat[magic_num] + ': ' + 'Stack opened: ' + currency + ' (' + dirxn.upper() + ')')
                            time.sleep(3)
                        else:
                            telegram_bot_sendtext(port_dict[port]+'-'+strat[magic_num] + ': ' + 'Stack failed. ' + (MT.order_return_message).upper() + ' For ' + currency + ' (' + dirxn.upper() + ')')
                
                if distance >= 3*atr:
                    if current_sl > new_sl:
                        move_sl_order = MT.Set_sl_and_tp_for_order(ticket=ticket, stoploss=new_sl, takeprofit=0)
                        if move_sl_order != -1:
                            telegram_bot_sendtext(strat[magic_num] + ': ' + 'SL moved:' + currency + ' (' + dirxn.upper() + ')')
                        else:
                            telegram_bot_sendtext(strat[magic_num] + ': ' + 'SL move failed. ' + (MT.order_return_message).upper() + ' For ' + currency + ' (' + dirxn.upper() + ')')
            elif dirxn == 'buy':
                limit_price = current_price - (0.5*atr)
                distance = current_price - open_price
                new_sl = limit_price - (1.5*atr)
                if distance >= 2*atr:
                    max_positions = distance//(2*atr) + 1
                    if currency_open_positions < max_positions:
                        order = MT.Open_order(instrument=currency, ordertype=(dirxn+'_limit'), volume=vol, openprice = limit_price, slippage = 10, magicnumber=magic_num, stoploss=new_sl, takeprofit=0, comment ='stack_v1')
                        if order != -1 or move_sl_order != -1:    
                            telegram_bot_sendtext(port_dict[port]+'-'+strat[magic_num] + ': ' + 'Stack opened: ' + currency + ' (' + dirxn.upper() + ')')
                            time.sleep(3)
                        else:
                            telegram_bot_sendtext(port_dict[port]+'-'+ strat[magic_num] + ': ' + 'Stack failed. ' + (MT.order_return_message).upper() + ' For ' + currency + ' (' + dirxn.upper() + ')')
                
                if distance >= 3*atr:
                    if current_sl < new_sl:
                        move_sl_order = MT.Set_sl_and_tp_for_order(ticket=ticket, stoploss=new_sl, takeprofit=0)
                        if move_sl_order != -1:
                            telegram_bot_sendtext(port_dict[port]+'-'+strat[magic_num] + ': ' + 'SL moved:' + currency + ' (' + dirxn.upper() + ')')
                        else:
                            telegram_bot_sendtext(port_dict[port]+'-'+strat[magic_num] + ': ' + 'SL move failed. ' + (MT.order_return_message).upper() + ' For ' + currency + ' (' + dirxn.upper() + ')')
                    
        return "All done for " + port_dict[port]
    else:
        return "No open positions. " + port_dict[port]


if datetime.now().weekday() > 5: #don't run on weekends
    exit()
elif datetime.now().weekday() == 5 and datetime.now().hour > 5: #last saturday 5am
    exit()
elif datetime.now().weekday() == 0 and datetime.now().hour < 5: #monday before 5am
    exit()
else:
    pass

for port in ports:
    status = stack(port)
    print(status)

telegram_bot_sendtext('Stacker done. ')