#stacker

from os import stat
import pandas as pd
import requests
from datetime import date, datetime
import time
from pathlib import Path
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
ports = [1122, 1125, 1127]
port_dict = {1122:'FTMO', 1125:'FXCM', 1127:'GP'}

list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCAD','GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'NZDCHF', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair
strat = {41:'CBR', 42:'SWB', 43:'ODN'}

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
    open_positions = MT.Get_all_open_positions()
    if len(open_positions) > 0:
        for currency in open_positions['instrument']:
            # print(currency)
            currency_open_positions = len(open_positions[open_positions['instrument']==currency])
            atr = currency_data['atr'][currency_data['Currency'] == currency].values[0]
            current_price = MT.Get_last_tick_info(instrument=currency)['bid']
            open_price = open_positions['open_price'][open_positions['instrument'] == currency].values[0]
            dirxn = open_positions['position_type'][open_positions['instrument'] == currency].values[0]
            magic_num = open_positions['magic_number'][open_positions['instrument'] == currency].values[0]
            vol = magic_num = open_positions['volume'][open_positions['instrument'] == currency].values[0]
            if dirxn == 'sell':
                limit_price = current_price + (0.5*atr)
                distance = open_price - current_price
                if distance > 2*atr:
                    max_positions = distance//(2*atr)
                    if max_positions < currency_open_positions:
                        order = MT.Open_order(instrument=currency, ordertype=(dirxn+'_limit'), volume=vol, openprice = limit_price, slippage = 10, magicnumber=magic_num, stoploss=0, takeprofit=0, comment ='stack_v1')
                        if order != -1:    
                            telegram_bot_sendtext(strat[magic_num] + ': ' + 'Stack opened: ' + pair + ' (' + dirxn.upper() + ')')
                            time.sleep(3)
                        else:
                            telegram_bot_sendtext(strat[magic_num] + ': ' + 'Stack failed. ' + (MT.order_return_message).upper() + ' For ' + pair + ' (' + dirxn.upper() + ')')
            elif dirxn == 'buy':
                limit_price = current_price - (0.5*atr)
                distance = current_price - open_price
                if distance > 2*atr:
                    max_positions = distance//(2*atr)
                    if max_positions < currency_open_positions:
                        order = MT.Open_order(instrument=currency, ordertype=(dirxn+'_limit'), volume=vol, openprice = limit_price, slippage = 10, magicnumber=magic_num, stoploss=0, takeprofit=0, comment ='stack_v1')
                        if order != -1:    
                            telegram_bot_sendtext(strat[magic_num] + ': ' + 'Stack opened: ' + pair + ' (' + dirxn.upper() + ')')
                            time.sleep(3)
                        else:
                            telegram_bot_sendtext(strat[magic_num] + ': ' + 'Stack failed. ' + (MT.order_return_message).upper() + ' For ' + pair + ' (' + dirxn.upper() + ')')
    return "All done for " + port_dict[port]


for port in ports:
    status = stack(port)
    print(status)