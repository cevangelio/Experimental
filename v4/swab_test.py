import pandas as pd
import pandas_ta as ta
import numpy as np
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
port = 1122 #FXCM MAIN 50k 1:100
# list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCAD','GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
list_symbols = ['EURCAD', 'USDCHF', 'CHFJPY', 'GBPJPY', 'EURCHF', 'EURGBP', 'GBPCHF', 'GBPUSD', 'EURUSD', 'EURJPY', 'USDCAD', 'USDJPY']
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

trend = []
for line in range(0, len(df_raw)):
    if df_raw['Current Price'].loc[line] > df_raw['EMA'].loc[line]:
        trend.append('buy')
    elif df_raw['Current Price'].loc[line] < df_raw['EMA'].loc[line]:
        trend.append('sell')
    else:
        trend.append('ignore')

df_raw['Trend'] = trend

test_1 = abs((np.array(df_raw['Current Price']) - np.array(df_raw['EMA']))/np.array(df_raw['EMA']))*1000

df_raw['str_test_1'] = test_1

df_raw.sort_values(by =['str_test_1'], ascending = False, inplace=True)
df_raw.reset_index(inplace=True)
df_raw.drop(columns = 'index', inplace=True)

top_pair = df_raw['Currency'].loc[0]
top_pair_trend = ''
if df_raw['Current Price'].loc[0] > df_raw['EMA'].loc[0]:
    top_pair_trend = 'buy'
elif df_raw['Current Price'].loc[0] < df_raw['EMA'].loc[0]:
    top_pair_trend = 'sell'
else:
    top_pair_trend = 'error'

#get hedges

hedge_options = [
['EURCHF', 'CHFJPY', 'EURJPY'], 
['GBPCHF', 'CHFJPY', 'GBPJPY'],
['USDCHF', 'CHFJPY', 'USDJPY'],
['EURGBP', 'GBPCHF', 'EURCHF'],
['EURUSD', 'USDCHF', 'EURCHF'],
['EURGBP', 'GBPJPY', 'EURJPY'],
['EURGBP', 'GBPUSD', 'EURUSD'],
['EURUSD', 'USDJPY', 'EURJPY'],
['GBPUSD', 'USDCHF', 'GBPCHF'],
['GBPUSD', 'USDJPY', 'GBPJPY'],
['USDCAD', 'EURUSD', 'EURCAD']
]

for items in hedge_options:
    if top_pair not in items:
        hedge_options.remove(items)
