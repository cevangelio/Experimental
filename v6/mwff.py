
import pandas as pd
import datetime
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
# ports = [1122, 1125, 1127]
port_dict = {1122:'FTMO', 1125:'FXCM', 1127:'GP'}

list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCAD','GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair

con = MT.Connect(server='127.0.0.1', port=1127, instrument_lookup=symbols)

tf = 'D1'
currency = 'GBPJPY'
bars = pd.DataFrame(MT.Get_last_x_bars_from_now(instrument = currency, timeframe = MT.get_timeframe_value(tf), nbrofbars=900))
rsi_trend_raw = ta.rsi(bars['close'], length = 100)
bars['rsi trend'] = rsi_trend_raw

conv_date = []
conv_day = []
for ep_time in bars['date']:
    conv = datetime.fromtimestamp(ep_time).strftime('%Y-%m-%d %H:%M:%S')
    day = datetime.fromtimestamp(ep_time).strftime('%A')
    conv_date.append(conv)
    conv_day.append(day)
bars['normal_date'] = conv_date
bars['day'] = conv_day


mwf = pd.DataFrame()
mwf['monday open'] = bars['open'][bars['day'] == 'Monday']
mwf.reset_index(inplace=True)
wed_open = []
fri_close = []
rsi_trend = []

for line in range(0, len(mwf)-1):
    try:
        rsi_raw = bars['rsi trend'].loc[mwf.loc[line]['index']+1] #tuesday RSI
        if rsi_raw > 50:
            rsi_trend.append('buy')
        elif rsi_raw < 50:
            rsi_trend.append('sell')
        else:
            rsi_trend.append('ignore')
        
        wed_raw = bars['open'].loc[mwf.loc[line]['index']+2]
        wed_open.append(wed_raw)
        fri_raw = bars['close'].loc[mwf.loc[line]['index']+4]
        fri_close.append(fri_raw)
    except:
        mwf.drop([mwf.loc[line]], inplace=True)

mwf['rsi_trend'] = rsi_trend
mwf['wed_open'] = wed_open
mwf['fri_close'] = fri_close

#get shortest

mon_open = []
wed_open = []
fri_close = []
for line in range(1, len(bars)-1):
    try:
        mon_open.append(bars['open'].loc[line])
        wed_open.append(bars['open'].loc[line + 2])
        fri_close.append(bars['close'].loc[line + 4])
    except:
        mon_open.append('ignore')
        wed_open.append('ignore')
        fri_close.append('ignore')