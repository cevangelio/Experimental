#check news
import pandas as pd
import datetime
from datetime import datetime, timedelta
from pathlib import Path

def pair_name(currency):
    symbol_dict = {'g':'GBP', 'j':'JPY', 'u':'USD','c':'CAD', 
    'f':'CHF','e':'EUR', 'a':'AUD', 'x':'XAU', 'n':'NZD'}
    first = symbol_dict[list(currency)[0]]
    second = symbol_dict[list(currency)[1]]
    fx_currency = first + second
    return fx_currency

home = str(Path.home())

curr_to_avoid_raw =[]
fx_calendar = pd.read_csv(home+'\Desktop\Fx_calendar_2b_raw.csv')
today = datetime.now()
curr_to_avoid_time = fx_calendar[['Currency', 'Converted']][(fx_calendar['Date']==today.strftime('%m/%d/%Y')) & (fx_calendar['Time']>today.strftime('%H:%M'))]
curr_to_avoid_time.reset_index(inplace=True)
curr_to_avoid_time.drop(columns = ['index'],inplace=True)
for line in curr_to_avoid_time['Converted']:
    test = datetime.now() + timedelta(hours = 8) <= datetime.strptime(line, '%m/%d/%Y %H:%M') <= datetime.now() + timedelta(hours = 8) #OG algo
    if test == True:
        curr_to_avoid_raw.append(curr_to_avoid_time['Currency'][curr_to_avoid_time['Converted'] == line].values[0])

def check_news(currency):
    currency_1 = currency[:3]
    currency_2 = currency[3:6]
    events = []
    events.append(curr_to_avoid_time[curr_to_avoid_time['Currency'] == currency_1].values.tolist())
    events.append(curr_to_avoid_time[curr_to_avoid_time['Currency'] == currency_2].values.tolist())
    if currency_1 in curr_to_avoid_raw:
        return True, events
    elif currency_2 in curr_to_avoid_raw:
        return True, events
    else:
        return False