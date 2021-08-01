'''
source: best scalping strategy period by moving average

rsi - len:14, 50 (same tf)
smoothed MA (30,50,200)- must be sloping, price above all 3
williams fractal - tapy or when price is nearest 30, around 5-10% distance(?)
tf = 5 min
exit = 10 pips?
stop = below low of prev candle


new rule
if below smma200 and rsi100 <50 and bear frac = sell
if above smma200 and rsi100 >50 and bull frac = buy
sl = 3atr
tp = 5atr
vol = 0.10 on 5k

'''

import pandas as pd
import requests
import datetime
from datetime import date, datetime
from pathlib import Path
import pandas_ta as ta
from tapy import Indicators
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
port = 1125 #FXCM MAIN 50k 1:100
list_symbols = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'CHFJPY', 'GBPAUD', 'GBPCAD','GBPCHF', 'GBPJPY', 'GBPUSD', 'NZDCAD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
symbols = {}
for pair in list_symbols:
    symbols[pair] = pair
con = MT.Connect(server='127.0.0.1', port=port, instrument_lookup=symbols)

home = str(Path.home())
t_gram_creds = open((home+'/Desktop/t_gram.txt'), 'r')
bot_token = t_gram_creds.readline().split('\n')[0]
bot_chatID = t_gram_creds.readline()
t_gram_creds.close()

def telegram_bot_sendtext(bot_message):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

def fractal(df):
    periods = (-2, -1, 1, 2)  
    bear_fractal = pd.Series(np.logical_and.reduce([
        df['high'] > df['high'].shift(period) for period in periods
    ]), index=df.index)
    bull_fractal = pd.Series(np.logical_and.reduce([
        df['low'] < df['low'].shift(period) for period in periods
    ]), index=df.index)
    return bear_fractal, bull_fractal

def scalp():
    df_raw = pd.DataFrame()
    df_raw['Currency'] = list_symbols
    current_price_l = []
    smma200_l = []
    rsi_raw_l = []
    bear_fractal_l = []
    bull_fractal_l = []
    atr_l = []
    for currency in df_raw['Currency']:
        bars = pd.DataFrame(MT.Get_last_x_bars_from_now(instrument = currency, timeframe = MT.get_timeframe_value('M5'), nbrofbars=600))
        current_price_l.append(bars['close'].loc[len(bars) - 1])
        i = Indicators(bars)
        # i.smma(period=30, column_name = 'smma30', apply_to = 'close')
        # i.smma(period=50, column_name = 'smma50', apply_to = 'close')
        i.smma(period=200, column_name = 'smma200', apply_to = 'close')
        rsi_raw = ta.rsi(bars['close'], length = 100)
        df = i.df
        df['rsi'] = rsi_raw
        df['bear_frac'], df['bull_frac'] = fractal(df)
        smma200_l.append(df.loc[len(df)-2]['smma200'])
        rsi_raw_l.append(df.loc[len(df)-2]['rsi'])
        bear_fractal_l.append(df.loc[len(df)-3]['bear_frac'])
        bull_fractal_l.append(df.loc[len(df)-3]['bull_frac'])
        atr_raw = ta.atr(high = bars['high'], low = bars['low'], close = bars['close'],mamode = 'EMA')
        bars['atr'] = atr_raw
        atr = atr_raw[len(bars) - 2] #last value
        atr_l.append(atr)
    df_raw['current price'] = current_price_l
    df_raw['smma200'] = smma200_l
    df_raw['rsi'] = rsi_raw_l
    df_raw['bear_fractal'] = bear_fractal_l
    df_raw['bull_fractal'] = bull_fractal_l
    df_raw['atr'] = atr_l
    smma_trend = []
    rsi_trend = []
    fractal_trend = []
    for line in range(0, len(df_raw)):
        if df_raw['current price'].loc[line] < df_raw['smma200'].loc[line]:
            smma_trend.append('sell')
        elif df_raw['current price'].loc[line] > df_raw['smma200'].loc[line]:
            smma_trend.append('buy')
        else:
            smma_trend.append('ignore')
    
        if df_raw['rsi'].loc[line] < 50:
            rsi_trend.append('sell')
        elif df_raw['rsi'].loc[line] > 50:
            rsi_trend.append('buy')
        else:
            rsi_trend.append('ignore')
        
        if df_raw['bear_fractal'].loc[line] == False and df_raw['bull_fractal'].loc[line] == True:
            fractal_trend.append('buy')
        elif df_raw['bear_fractal'].loc[line] == True and df_raw['bull_fractal'].loc[line] == False:
            fractal_trend.append('sell')
        else:
            fractal_trend.append('ignore')

    df_raw['smma trend'] = smma_trend
    df_raw['rsi trend'] = rsi_trend
    df_raw['fractal trend'] = fractal_trend

    action = []
    for line in range(0, len(df_raw)):
        if (df_raw['smma trend'].loc[line] == 'sell') and (df_raw['rsi trend'].loc[line] == 'sell') and (df_raw['fractal trend'].loc[line] == 'sell'):
            action.append('sell')
        elif (df_raw['smma trend'].loc[line] == 'buy') and (df_raw['rsi trend'].loc[line] == 'buy') and (df_raw['fractal trend'].loc[line] == 'buy'):
            action.append('buy')
        else:
            action.append('ignore')
    df_raw['Action'] = action
    df_raw['comment'] = 'cherokee'
    sl = []
    tp = []
    for line in range(0, len(df_raw)):
        if df_raw['Action'].loc[line] == 'buy':
            sl.append((df_raw['current price'].loc[line]) - (3.3*(df_raw['atr'].loc[line])))
            tp.append((df_raw['current price'].loc[line]) + (5*(df_raw['atr'].loc[line])))
        elif df_raw['Action'].loc[line] == 'sell':
            sl.append((df_raw['current price'].loc[line]) + (3.3*(df_raw['atr'].loc[line])))
            tp.append((df_raw['current price'].loc[line]) - (5*(df_raw['atr'].loc[line])))
        else:
            sl.append(0)
            tp.append(0)
    df_raw['sl'] = sl
    df_raw['tp'] = tp
    return df_raw

df = scalp()
print(df)

to_trade = df[df['Action'] != 'ignore']
to_trade.reset_index(inplace = True)
to_trade.drop(columns = 'index', inplace = True)

for pair in to_trade['Currency']:
    current_price = to_trade['current price'][to_trade['Currency'] == pair].values[0]
    dirxn = to_trade['Action'][to_trade['Currency'] == pair].values[0]
    sloss = round(to_trade['sl'][to_trade['Currency'] == pair].values[0],5)
    tprof = round(to_trade['tp'][to_trade['Currency'] == pair].values[0],5)
    spread = MT.Get_last_tick_info(instrument=pair)['spread']
    coms = to_trade['comment'][to_trade['Currency'] == pair].values[0]

    # vol = round((MT.Get_dynamic_account_info()['balance']*0.000010), 2)
    vol = 0.03
    if spread <= 130.0:
        order = MT.Open_order(instrument=pair, ordertype=dirxn, volume=vol, openprice = 0.0, slippage = 10, magicnumber=41, stoploss=sloss, takeprofit=tprof, comment =coms)
        if order != -1:
            print('Order success! ' + pair + ' (' + dirxn.upper() + ')')
        else:
            print('Error! ' + pair + ' (' + dirxn.upper() + ')')
        #     telegram_bot_sendtext('Cerberus setup found. Position opened successfully: ' + pair + ' (' + dirxn.upper() + ')')
        #     telegram_bot_sendtext('Price: ' + str(current_price) + ', SL: ' + str(sloss) + ', TP: ' + str(tprof))
        #     time.sleep(3)
        # else:
        #     telegram_bot_sendtext('Cerberus setup found. ' + (MT.order_return_message).upper() + ' For ' + pair + ' (' + dirxn.upper() + ')')
    # else:
    #     limit_order = MT.Open_order(instrument=pair, ordertype=(dirxn+'_limit'), volume=vol, openprice = limit_price, slippage = 10, magicnumber=41, stoploss=sloss, takeprofit=tprof, comment =coms+'LMT')
    #     if limit_order != -1:
    #         telegram_bot_sendtext('Cerberus setup found but spread too high. ' + pair + ' (' + dirxn.upper() + ' LIMIT), spread: ' + str(spread))
    #         telegram_bot_sendtext('Price: ' + str(limit_price) + ', SL: ' + str(sloss) + ', TP: ' + str(tprof))
    #     else:
    #         telegram_bot_sendtext('Cerberus setup found but spread too high. ' + (MT.order_return_message).upper() + ' For ' + pair + ' (' + dirxn.upper() + ' LIMIT)')
    #         telegram_bot_sendtext('Price: ' + str(limit_price) + ', SL: ' + str(sloss)+ ', TP: ' + str(tprof))


# telegram_bot_sendtext('No issues')