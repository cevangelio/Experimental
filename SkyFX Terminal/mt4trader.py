#mt4 trader

from Pytrader_API_V1_06 import *
MT = Pytrader_API()
port = 1125

def trade(dirxn, symbol, volume=0.01, sl=0, tp=0, comment=''):
    con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup={symbol:symbol})
    new_order = MT.Open_order(instrument=symbol, ordertype=dirxn, volume=volume, openprice = 0.0, slippage = 10, magicnumber=41, stoploss=0.0, takeprofit=0.0, comment = comment)
    if new_order > 0:
        return "Order opened for " + symbol + " (" + dirxn.capitalize() + ")."
    else:
        return "Order opening for " + symbol + " failed."