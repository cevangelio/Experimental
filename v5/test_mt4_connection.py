#test connection

from Pytrader_API_V1_06 import *
MT = Pytrader_API()
port = [1122, 1125, 1127] #FXCM MAIN 50k 1:100
port_dict = {1122:'FTMO', 1125:'FXCM', 1127:'Global_Prime'}
list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair

for mt4 in port:
    con = MT.Connect(server='127.0.0.1', port=mt4, instrument_lookup=symbols)
    if con == True:
        pera = MT.Get_dynamic_account_info()['balance']
        positions = MT.Get_all_open_positions()
        print(port_dict[mt4], 'MT4 connection is working. Your current balance is', str(pera), 'with' , len(positions), 'total positions open.')
