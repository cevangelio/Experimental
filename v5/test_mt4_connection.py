#test connection

from Pytrader_API_V1_06 import *
MT = Pytrader_API()
port = [1122, 1125, 1127] #FXCM MAIN 50k 1:100
list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair

for mt4 in port:
    con = MT.Connect(server='127.0.0.1', port=mt4, instrument_lookup=symbols)
    if con == True:
        print('MT4 connection working.')
        pera = MT.Get_dynamic_account_info()['balance']
        print('Your current balance is ' + str(pera))
        positions = MT.Get_all_open_positions()
        print(len(positions[positions['instrument'] == 'AUDUSD']))