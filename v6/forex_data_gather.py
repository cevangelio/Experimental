from Pytrader_API_V1_06 import *
MT = Pytrader_API()
ports = [1122, 1125, 1127, 1129, 1131, 1133, 1135]
port_dict = {1122:'FTMO_Live', 1125:'FXCM_Demo', 1127:'GP_Live', 1129:'GP_Demo', 1131:'FTMO_Demo', 1133:'FTMO_DEMO_2', 1135:'FTMO_DEMO_3'}

list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCAD','GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY','SGDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair

def get_data(currency,port=0):
    con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup=symbols)
    history = MT.Get_last_x_bars_from_now(instrument = currency, timeframe = MT.get_timeframe_value('W1'), nbrofbars=300)
    while history == None:
        history = MT.Get_last_x_bars_from_now(instrument = currency, timeframe = MT.get_timeframe_value('W1'), nbrofbars=300)
        print(currency, ' gathering data.')
    else:
        print(currency, ' data complete.')

for pair in list_symbols:
    for port in ports:
        try:
            get_data(pair,port) #change port here
        except:
            print('Port inactive.')