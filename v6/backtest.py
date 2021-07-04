
import pandas as pd
import pandas_ta as ta
import datetime
from datetime import datetime
import time
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
port = 1122 #FXCM MAIN 50k 1:100
list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCAD','GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair
con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup=symbols)

# def backtest(df):
#     total_trades = len(df[df['Action'] !=0])
#     for line in range(0, len(df)):
#         if df['Action'].loc[line].values[0] != 0: #buy
#             open_price = df['open'].loc[line].values[0]
#             sl = df[]


#     return total_trades, win_trades, loss_trade

currency = 'EURUSD'
tf = 'D1'
x_bars = 3000
bars = pd.DataFrame(MT.Get_last_x_bars_from_now(instrument = currency, timeframe = MT.get_timeframe_value(tf), nbrofbars=x_bars))
atr_raw = ta.atr(high = bars['high'], low = bars['low'], close = bars['close'],mamode = 'EMA')
atr_raw = ta.atr(high = bars['high'], low = bars['low'], close = bars['close'],mamode = 'EMA')
bars['atr'] = atr_raw
rsi_raw = ta.rsi(bars['close'], length = 14)
bars['rsi'] = rsi_raw
rsi_trend_raw = ta.rsi(bars['close'], length = 100)
bars['rsi trend'] = rsi_trend_raw
macd_raw = ta.macd(bars['close'])
macd_final = pd.concat([bars,macd_raw], axis=1, join='inner')
df_raw = macd_final
macd_trend = []
for line in range(0, len(df_raw)):
    if df_raw['MACD_12_26_9'].loc[line] < 0 and df_raw['MACDs_12_26_9'].loc[line] < 0:
        if df_raw['MACD_12_26_9'].loc[line] > df_raw['MACDs_12_26_9'].loc[line]:
            macd_trend.append('buy')
        else:
            macd_trend.append('ignore')
    elif df_raw['MACD_12_26_9'].loc[line] > 0 and df_raw['MACDs_12_26_9'].loc[line] > 0:
        if df_raw['MACD_12_26_9'].loc[line] < df_raw['MACDs_12_26_9'].loc[line]:
            macd_trend.append('sell')
        else:
            macd_trend.append('ignore')
    else:
        macd_trend.append('ignore')
df_raw['Current MACD Trend'] = macd_trend

rsi_trend_logic = []
for line in range(1, len(df_raw)):
    rsi_score_raw = df_raw['rsi trend'].loc[line]
    rsi_score_raw_prev = df_raw['rsi trend'].loc[line-1]
    if rsi_score_raw > 50:
        rsi_trend_logic.append('buy')
    elif rsi_score_raw < 50:
        rsi_trend_logic.append('sell')
    else:
        rsi_trend_logic.append('ignore')
rsi_trend_logic.insert(0, 'ignore')
df_raw['RSI 100'] = rsi_trend_logic
rsi_status = []
for line in range(1, len(df_raw)):
    rsi_status_raw = df_raw['rsi'].loc[line]
    rsi_status_raw_prev = df_raw['rsi'].loc[line-1]
    if rsi_status_raw_prev >= 70 and rsi_status_raw < 70:
        rsi_status.append('sell')
    elif rsi_status_raw_prev <= 30 and rsi_status_raw > 30:
        rsi_status.append('buy')
    elif rsi_status_raw_prev >= 50 and rsi_status_raw < 50:
        rsi_status.append('sell')
    elif rsi_status_raw_prev <= 50 and rsi_status_raw > 50:
        rsi_status.append('buy')
    else:
        rsi_status.append('ignore')
rsi_status.insert(0,'ignore')
df_raw['RSI 14'] = rsi_status
trade_status = []
for line in range(0, len(df_raw)):
    if df_raw['RSI 100'].loc[line] == 'buy' and df_raw['RSI 14'].loc[line] == 'buy' and df_raw['Current MACD Trend'].loc[line] == 'buy':
        trade_status.append(1)
    elif df_raw['RSI 100'].loc[line] == 'sell' and df_raw['RSI 14'].loc[line] == 'sell' and df_raw['Current MACD Trend'].loc[line] == 'sell':
        trade_status.append(-1)
    else:
        trade_status.append(0)
df_raw['Action'] = trade_status
df_raw['datetime'] = [time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch_time)) for epoch_time in df_raw['date']]
sl = []
tp = []
for line in range(0, len(df_raw)):
    if df_raw['Action'].loc[line] == 1:
        sl.append(df_raw['open'].loc[line+1] - (3*(df_raw['atr'].loc[line])))
        tp.append(df_raw['open'].loc[line+1] + (3*(df_raw['atr'].loc[line])))
    elif df_raw['Action'].loc[line] == -1:
        sl.append(df_raw['open'].loc[line+1] + (3*(df_raw['atr'].loc[line])))
        tp.append(df_raw['open'].loc[line+1] - (3*(df_raw['atr'].loc[line])))
    else:
        sl.append(0)
        tp.append(0)
df_raw['sl'] = sl
df_raw['tp'] = tp
print(len(df_raw[df_raw['Action'] != 0]))
print(df_raw[df_raw['Action'] != 0])
