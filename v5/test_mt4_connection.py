#test connection

from Pytrader_API_V1_06 import *
MT = Pytrader_API()
<<<<<<< HEAD
port = [1122, 1125, 1127, 1129] #FXCM MAIN 50k 1:100
port_dict = {1122:'FTMO', 1125:'FXCM', 1127:'Global_Prime', 1129:'Global_Prime_Demo'}
=======
port = [1122, 1125, 1127, 1129, 1131] #FXCM MAIN 50k 1:100
port_dict = {1122:'FTMO_Live', 1125:'FXCM_DEMO', 1127:'GP_Live', 1129: 'GP_DEMO', 1131:'FTMO_DEMO'}
>>>>>>> 31420563c4eb47d0ef00bd710d125b13ccadf61c
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
    else:
        print(port_dict[mt4], 'Not working')
