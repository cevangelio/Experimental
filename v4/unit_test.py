import pandas as pd
import pandas_ta as ta
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
port = 1122 #FXCM MAIN 50k 1:100
list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCAD','GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair
con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup=symbols)

x_bars = 600
currency = 'EURUSD'
bars = pd.DataFrame(MT.Get_last_x_bars_from_now(instrument = currency, timeframe = MT.get_timeframe_value('H1'), nbrofbars=x_bars))
ema_raw = ta.ema(bars['close'], length = 200)
bars['ema'] = ema_raw
atr_raw = ta.atr(high = bars['high'], low = bars['low'], close = bars['close'],mamode = 'EMA')
bars['atr'] = atr_raw
rsi_raw = ta.rsi(bars['close'], length = 14)
bars['rsi'] = rsi_raw
macd_raw = ta.macd(bars['close'])
macd_final = pd.concat([bars,macd_raw], axis=1, join='inner')

#analysis needed
trend = []
atr = []
rsi = []
macd = []