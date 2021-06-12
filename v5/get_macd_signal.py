import pandas as pd
from datetime import datetime
from pathlib import Path
import pandas_ta as ta
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
port = 1122 #FXCM MAIN 50k 1:100
list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair
con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup=symbols)

def get_signal(currency, tf='H1', x_bars=600):
    bars = pd.DataFrame(MT.Get_last_x_bars_from_now(instrument = currency, timeframe = MT.get_timeframe_value('H1'), nbrofbars=x_bars))
    current_price = bars['close'].loc[len(bars) - 1]
    ema_raw = ta.ema(bars['close'], length = 200)
    ema = ema_raw[len(bars) - 1] #last value
    macd_raw = ta.macd(bars['close'])
    macd_final = pd.concat([bars,macd_raw], axis=1, join='inner')
    macd_curr = macd_final.loc[len(bars) - 1]['MACD_12_26_9']
    macd_signal_curr = macd_final.loc[len(bars) - 1]['MACDs_12_26_9']
    macd_prev = macd_final.loc[len(bars) - 6]['MACD_12_26_9']
    macd_signal_prev = macd_final.loc[len(bars) - 6]['MACDs_12_26_9']
    trend = ''
    if current_price > ema:
        trend = 'buy'
    elif current_price < ema:
        trend = 'sell'
    else:
        trend = 'ignore'
    macd_trend = ''
    if macd_curr < 0 and macd_signal_curr < 0:
        if macd_curr > macd_signal_curr:
            macd_trend = 'buy'
        elif macd_curr < macd_signal_curr:
            macd_trend = 'sell'
        else:
            macd_trend = 'ignore'
    else:
        macd_trend = 'ignore'
    prev_macd_trend = ''
    if macd_prev < 0 and macd_signal_prev < 0:
        if macd_prev > macd_signal_prev:
            prev_macd_trend = 'buy'
        elif macd_prev < macd_signal_prev:
            prev_macd_trend = 'sell'
        else:
            prev_macd_trend = 'ignore'
    else:
        prev_macd_trend = 'ignore'
    return trend, macd_trend, prev_macd_trend