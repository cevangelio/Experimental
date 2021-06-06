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

df_raw = pd.DataFrame()
df_raw['Currency'] = list_symbols

current_price_l = []
ema_l = []
x_bars = 600
for currency in df_raw['Currency']:
    bars = pd.DataFrame(MT.Get_last_x_bars_from_now(instrument = currency, timeframe = MT.get_timeframe_value('H1'), nbrofbars=x_bars))
    current_price = bars['close'].loc[len(bars) - 1]
    current_price_l.append(current_price)
    ema_raw = ta.ema(bars['close'], length = 200)
    bars['ema'] = ema_raw
    ema = ema_raw[len(bars) - 1] #last value
    ema_l.append(ema)

df_raw['Current Price'] = current_price_l
df_raw['EMA'] = ema_l

dist_from_ema = []

for line in range(0, len(df_raw)):
    

