
import pandas as pd
import datetime
from datetime import date, datetime
import time
from pathlib import Path
import dateutil.relativedelta
from Pytrader_API_V1_06 import *
MT = Pytrader_API()
port = 1122 #FXCM MAIN 50k 1:100
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

df_journal = pd.read_csv('d:/TradeJournal/trade_journal.csv')
df_close_positions = MT.Get_all_closed_positions()
df_close_journal = pd.DataFrame()

# pd.read_csv('d:/TradeJournal/X_trade_journal.csv')

#iterate from journal done
#get all data needed [results,PNL, open, close, duration] done
#append completed info to x_journal 
#delete completed in df_journal done

result = []
pnl = []
open_time = []
close_time = []
duration = []
for comment in df_journal['comment']:
    try:
        pnl_raw = df_close_positions['profit'][df_close_positions['comment'] == comment].values[0]
        pnl.append(pnl_raw)
        if pnl_raw > 0:
            result.append('win')
        else:
            result.append('lose')
        open_raw = df_close_positions['open_time'][df_close_positions['comment'] == comment].values[0]
        close_raw = df_close_positions['close_time'][df_close_positions['comment'] == comment].values[0]   
        open_time.append(time.strftime('%Y-%m-%d %A %H:%M:%S', time.localtime(open_raw)))
        close_time.append(time.strftime('%Y-%m-%d %A %H:%M:%S', time.localtime(close_raw)))
        duration_raw = dateutil.relativedelta.relativedelta(datetime.fromtimestamp(close_raw), datetime.fromtimestamp(open_raw))
        duration.append((str(duration_raw.days) + ' days', str(duration_raw.hours) + ' hours', str(duration_raw.minutes)+ ' mins'))
    except:
        pnl.append(0)
        result.append('no_take')
        open_time.append('unknown')
        close_time.append('unknown')
        duration.append('unknown')

df_journal['results'] = result
df_journal['PNL'] = pnl
df_journal['Open'] = open_time
df_journal['Close'] = close_time
df_journal['Duration'] = duration
df_close_journal = df_journal[df_journal['Close'] != 'unknown']
to_remove = df_journal.index[df_journal['Close'] != 'unknown'].tolist()
for line in to_remove:
    df_journal.drop([line], inplace=True)
df_journal.drop(columns=['results', 'PNL', 'Open', 'Close', 'Duration'], inplace=True)
df_journal.to_csv('d:/TradeJournal/trade_journal.csv', index=False)
df_close_journal_prev = pd.read_csv('d:/TradeJournal/X_trade_journal.csv')
df_close_journal_prev.append(df_close_journal)
df_close_journal_prev.to_csv('d:/TradeJournal/X_trade_journal.csv', index=False)