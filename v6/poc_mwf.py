
from sys import path
import pandas as pd
import numpy as np
from pandas.tseries.offsets import Nano
import pandas_ta as ta
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

analysis_all = pd.DataFrame(columns=['Currency', 'Total Winners', 'Total Win Pips', 'Average Win Pips', 'Total Losers', 'Total Lose Pips', 'Average Lose Pips', 'Win Rate', 'PNL'])

for currency in list_symbols:
    print('Stats for', currency)
    blank = pd.DataFrame()
    blank.to_excel('d:/TradeJournal/MWF/'+currency+'_mwf.xlsx', index=False)
    tf = 'D1'
    # currency = 'GBPJPY'
    bars = pd.DataFrame(MT.Get_last_x_bars_from_now(instrument = currency, timeframe = MT.get_timeframe_value(tf), nbrofbars=1200))
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
    mon_open= bars['open'][bars['day'] == 'Monday'] #181
    wed_open = list(bars['open'][bars['day'] == 'Wednesday']) #179
    wed_open.insert(0,0)
    wed_open.insert(0,0)
    fri_close = list(bars['close'][bars['day'] == 'Friday']) #180
    fri_close.insert(0,0)
    rsi = list(bars['rsi trend'][bars['day'] == 'Tuesday']) #179
    rsi.insert(0,0)
    rsi.insert(0,0)
    mwf['monday open'] = mon_open
    mwf['wed open'] = wed_open
    mwf['rsi'] = rsi
    mwf['fri close'] = fri_close
    rsi_trend = []
    for rsi in mwf['rsi']:
        if rsi > 50:
            rsi_trend.append('buy')
        elif rsi < 50:
            rsi_trend.append('sell')
        elif rsi == 0:
            rsi_trend.append('ignore')
        else:
            rsi_trend.append('ignore')
    mwf['rsi trend'] = rsi_trend
    mwf.reset_index(inplace=True)
    # mwf.drop(columns='index', inplace=True)

    action_raw = []
    for line in range(0, len(mwf)):
        if (mwf['monday open'].loc[line] > mwf['wed open'].loc[line]) and mwf['rsi trend'].loc[line] == 'sell': #og = mwf['rsi trend'].loc[line] == 'sell'
            action_raw.append('buy')
        elif (mwf['monday open'].loc[line] < mwf['wed open'].loc[line]) and mwf['rsi trend'].loc[line] == 'buy':  #og = mwf['rsi trend'].loc[line] == 'buy'
            action_raw.append('sell')
        else:
            action_raw.append('ignore')

    mwf['action raw'] = action_raw

    fri_results = []
    for line in range(0, len(mwf)):
        if mwf['fri close'].loc[line] > mwf['wed open'].loc[line]:
            fri_results.append('buy')
        elif mwf['fri close'].loc[line] < mwf['wed open'].loc[line]:
            fri_results.append('sell')
        else:
            fri_results.append('ignore')
    mwf['correct action'] = fri_results

    

    win_raw = []
    for line in range(0, len(mwf)):
        if mwf['action raw'].loc[line] != 'ignore':
            if ((mwf['action raw'].loc[line]) == (mwf['correct action'].loc[line])) == True:
                win_raw.append('win')
            else:
                win_raw.append('lose')
        else:
            win_raw.append('ignore')
    tick_size = MT.Get_instrument_info(instrument=currency)['point']
    mwf['pips'] = abs((np.array(mwf['wed open']) - np.array(mwf['fri close']))/tick_size)
    mwf['win_lose'] = win_raw
    mwf.drop([0,1], inplace=True)
    final_analysis = []
    final_analysis.append(currency)
    analysis = pd.DataFrame(columns=['Analysis'])
    analysis.loc[0] = 'Total winners: ' + str(len(mwf[mwf['win_lose'] == 'win']))
    final_analysis.append(len(mwf[mwf['win_lose'] == 'win']))
    analysis.loc[len(analysis) + 1] = 'Total win pips: ' + str((mwf['pips'][mwf['win_lose'] == 'win'].sum())/10)
    final_analysis.append((mwf['pips'][mwf['win_lose'] == 'win'].sum())/10)
    analysis.loc[len(analysis) + 1] = 'Average win pips: ' + str((mwf['pips'][mwf['win_lose'] == 'win'].mean())/10)
    final_analysis.append((mwf['pips'][mwf['win_lose'] == 'win'].mean())/10)
    analysis.loc[len(analysis) + 1] = 'Total losers: ' + str(len(mwf[mwf['win_lose'] == 'lose']))
    final_analysis.append(len(mwf[mwf['win_lose'] == 'lose']))
    analysis.loc[len(analysis) + 1] = 'Total lose pips: ' + str((mwf['pips'][mwf['win_lose'] == 'lose'].sum())/10)
    final_analysis.append((mwf['pips'][mwf['win_lose'] == 'lose'].sum())/10)
    analysis.loc[len(analysis) + 1] = 'Average lose pips: ' + str((mwf['pips'][mwf['win_lose'] == 'lose'].mean())/10)
    final_analysis.append((mwf['pips'][mwf['win_lose'] == 'lose'].mean())/10)
    analysis.loc[len(analysis) + 1] = 'Win Rate: ' + str(len(mwf[mwf['win_lose'] == 'win'])/(len(mwf[mwf['win_lose'] == 'win'])+len(mwf[mwf['win_lose'] == 'lose'])))
    final_analysis.append(len(mwf[mwf['win_lose'] == 'win'])/(len(mwf[mwf['win_lose'] == 'win'])+len(mwf[mwf['win_lose'] == 'lose'])))
    analysis.loc[len(analysis) + 1] = 'PNL: ' + str(((mwf['pips'][mwf['win_lose'] == 'win'].sum())/10) - ((mwf['pips'][mwf['win_lose'] == 'lose'].sum())/10))
    final_analysis.append(((mwf['pips'][mwf['win_lose'] == 'win'].sum())/10) - ((mwf['pips'][mwf['win_lose'] == 'lose'].sum())/10))
    if len(analysis_all) == 0:
        analysis_all.loc[0] = final_analysis
    else:
        analysis_all.loc[len(analysis_all)+1] = final_analysis
    path = 'd:/TradeJournal/MWF/'+currency+'_mwf.xlsx'
    writer = pd.ExcelWriter(path, engine = 'xlsxwriter')
    bars.to_excel(writer, sheet_name = 'raw_bars')
    mwf.to_excel(writer, sheet_name = 'mwf')
    analysis.to_excel(writer, sheet_name = 'analysis')
    writer.save()
    writer.close()

analysis_all.to_excel('d:/TradeJournal/MWF/mwf_all_analysis.xlsx', index=False)