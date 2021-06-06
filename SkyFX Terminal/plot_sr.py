#plot with SR

from datetime import datetime,timedelta
import pandas as pd
import time
import pymt5adapter as mt5
import pytz
import pandas_bokeh
import get_sr as gsr

pd.set_option('plotting.backend', 'pandas_bokeh')

def plot_sr(symbol):
    pandas_bokeh.output_file(symbol + " plot.html")
    timezone = pytz.timezone("Etc/UTC")
    mt5.initialize()
    rates = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_H1, datetime.now(), 242)
    rates_frame = pd.DataFrame(rates)
    rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
    levels = gsr.get_sr(symbol)
    ll = gsr.lower_level(gsr.get_current_price(symbol), levels=levels)
    ul = gsr.upper_level(gsr.get_current_price(symbol), levels=levels)
    rates_frame['lower level'] = [ll]*len(rates_frame)
    rates_frame['upper level'] = [ul]*len(rates_frame)
    rates_frame[['close', 'lower level', 'upper level']].plot(title=symbol + ' Plot')