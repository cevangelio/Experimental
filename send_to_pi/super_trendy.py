#Get Super Trendy every Hour

from tradingview_ta import TA_Handler, Interval
import pandas as pd
import time
from pathlib import Path
import requests
from bokeh.io import output_file, show, save
from bokeh.layouts import widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, StringFormatter, TableColumn
from bokeh.models import Title
import numpy as np

if datetime.now().weekday() > 4:
    exit()

home = str(Path.home())

t_gram_creds = open((home+'/Desktop/Experimental/t_gram.txt'), 'r')
bot_token = t_gram_creds.readline().split('\n')[0]
bot_chatID = t_gram_creds.readline()
t_gram_creds.close()

def telegram_bot_sendtext(bot_message):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

def telegram_bot_sendfile():
    url = "https://api.telegram.org/bot" + bot_token + "/sendDocument"
    files = {'document': open((home +'\Desktop\Experimental\signals_1012.html'), 'rb')}
    data = {'chat_id' : bot_chatID}
    r= requests.post(url, files=files, data=data)
    print(r.status_code, r.reason, r.content)

def get_senti(fx_currency, period):
    # print(fx_currency)
    handler = TA_Handler()
    handler.set_symbol_as(fx_currency)
    handler.set_exchange_as_forex()
    handler.set_screener_as_forex()
    if period == '15m':
        handler.set_interval_as(Interval.INTERVAL_15_MINUTES)
        analysis = handler.get_analysis().summary
        return analysis
    elif period == '4h':
        handler.set_interval_as(Interval.INTERVAL_4_HOURS)
        analysis = handler.get_analysis().summary
        return analysis
    elif period == '1h':
        handler.set_interval_as(Interval.INTERVAL_1_HOUR)
        analysis = handler.get_analysis().summary
        return analysis
    elif period == '1d':
        handler.set_interval_as(Interval.INTERVAL_1_DAY)
        analysis = handler.get_analysis().summary
        return analysis

def pair_name(currency):
    symbol_dict = {'g':'GBP', 'j':'JPY', 'u':'USD','c':'CAD', 
    'f':'CHF','e':'EUR', 'a':'AUD', 'x':'XAU', 'n':'NZD'}
    first = symbol_dict[list(currency)[0]]
    second = symbol_dict[list(currency)[1]]
    fx_currency = first + second
    return fx_currency

def sentiment_score(data):
    buy = list(data).count('BUY')
    sbuy = list(data).count('STRONG_BUY')
    sell = list(data).count('SELL')
    ssell = list(data).count('STRONG_SELL')
    total_score = buy + 3*sbuy + (-1*sell) + (-3*ssell)
    return total_score

fx_pairs = []
fx_raw =  ['ac', 'af', 'aj', 'au', 'cf', 'cj', 'ea', 'ec', 'ef', 'ej', 'eu', 'fj', 'ga', 'gc', 'gf', 'gj', 'gu', 'nc', 'nj', 'nu', 'uc', 'uf', 'uj']
for pair in fx_raw:
    fx_pairs.append(pair_name(pair))

df_pairs = pd.DataFrame(columns=['Currency', '15m', '1h', '4h', '1d'])
df_pairs['Currency'] = fx_pairs

min_15 = []
hour_1 = []
hour_4 = []
day_1 = []

for pair in df_pairs['Currency']:
    min_15.append(get_senti(pair,'15m')['RECOMMENDATION'])
    time.sleep(2)
    hour_1.append(get_senti(pair,'1h')['RECOMMENDATION'])
    time.sleep(2)
    hour_4.append(get_senti(pair,'4h')['RECOMMENDATION'])
    time.sleep(2)
    day_1.append(get_senti(pair, '1d')['RECOMMENDATION'])
    time.sleep(2)
    print("Done for " + pair + '.')

df_pairs['15m'] = min_15
df_pairs['1h'] = hour_1
df_pairs['4h'] = hour_4
df_pairs['1d'] = day_1

score = []
for x in range(0, len(df_pairs)):
    score.append(sentiment_score(df_pairs.loc[x]))
df_pairs['FX Score'] = score
df_pairs['FX Score converted'] = np.absolute(df_pairs['FX Score'])
df_pairs = df_pairs[df_pairs['FX Score converted'] >=10]]
trendy_pairs = str(df_pairs['Currency'])

if len(df_pairs) <1:
    exit()
else:
    pass

datatable = df_pairs
source = ColumnDataSource(datatable)
now = datetime.now().strftime("%H:%M %m/%d/%Y")
msg = 'Super Trendy as of ' + now + '.\n' + trendy_pairs + ' on fire.'

columns = [
        TableColumn(field="Currency", title=now, formatter=StringFormatter()),
        TableColumn(field="15m", title="15Minutes"),
        TableColumn(field="1h", title="1Hour"),
        TableColumn(field="4h", title="4Hours"),
        TableColumn(field="1d", title="1Day"), 
        TableColumn(field="FX Score", title="FX Score")
    ]
data_table = DataTable(source=source, columns=columns, width=len(df_pairs.columns)*120, height=((len(df_pairs)+2)*28))
try:
    save(data_table, title='Trend Scanner', filename=(home +'\Desktop\signals_1012.html'))
except:
    print(data_table)


telegram_bot_sendtext(msg)

try:
    telegram_bot_sendfile()
except:
    print('Data table failed.')

