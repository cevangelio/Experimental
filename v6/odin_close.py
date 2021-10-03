
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
ports = [1122, 1125, 1127]
port_dict = {1122:'FTMO', 1125:'FXCM', 1127:'GP'}

list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCAD','GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair
con = MT.Connect(server='127.0.0.1', port=1122, instrument_lookup=symbols)

positions = MT.Get_all_open_positions()

for tix in positions['ticket']:
    magic_num = positions['magic_number'][positions['ticket']==tix].values[0]
    if magic_num == 43:
        MT.Close_position_by_ticket(ticket=positions['ticket'][positions['instrument'] == pair].values[0])
