#scalper

import time
from get_senti import *
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
port = 1122 #FXCM MAIN 50k 1:100
list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair
con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup=symbols)

def trade(dirxn, symbol, volume=0.01, sl=0, tp=0, comment=''):
    con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup={symbol:symbol})
    new_order = MT.Open_order(instrument=symbol, ordertype=dirxn, volume=volume, openprice = 0.0, slippage = 10, magicnumber=41, stoploss=0.0, takeprofit=0.0, comment = comment)
    if new_order > 0:
        return "Order opened for " + symbol + " (" + dirxn.capitalize() + ")."
    else:
        return "Order opening for " + symbol + " failed."

senti = ''
currency = 'AUDJPY'
vol = 0.10
for x in range(0, 61):
    senti =  get_senti(currency, period='15m')
    print(senti)
    if senti['15m']== 'SELL':
        trade(dirxn='sell', symbol=currency, volume=vol)
        print('sell opened')
        time.sleep(60)
    elif senti['15m'] == 'STRONG_SELL':
        trade(dirxn='sell', symbol=currency, volume=vol)
        print('sell opened')
        time.sleep(60)
    elif senti['15m'] == 'BUY':
        trade(dirxn='buy', symbol=currency, volume=vol)
        print('buy opened')
        time.sleep(60)
    elif senti['15m'] == 'STRONG_BUY':
        trade(dirxn='buy', symbol=currency, volume=vol)
        print('buy opened')
        time.sleep(60)
    else:
        print('no trade')
        time.sleep(60)
    senti = ''

#started 7:53
