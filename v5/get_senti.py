##get senti
from tradingview_ta import TA_Handler, Interval
import time

def get_senti(fx_currency, period='all'):
    analysis_final = {}
    handler = TA_Handler()
    handler.set_symbol_as(fx_currency)
    handler.set_exchange_as_forex()
    handler.set_screener_as_forex()
    if period == '15m':
        handler.set_interval_as(Interval.INTERVAL_15_MINUTES)
        analysis = handler.get_analysis().summary
        analysis_final['15m'] = analysis['RECOMMENDATION']
    elif period == '4h':
        handler.set_interval_as(Interval.INTERVAL_4_HOURS)
        analysis = handler.get_analysis().summary
        analysis_final['4h'] = analysis['RECOMMENDATION']
    elif period == '1h':
        handler.set_interval_as(Interval.INTERVAL_1_HOUR)
        analysis = handler.get_analysis().summary
        analysis_final['1h'] = analysis['RECOMMENDATION']
    elif period == '1d':
        handler.set_interval_as(Interval.INTERVAL_1_DAY)
        analysis = handler.get_analysis().summary
        analysis_final['1d'] = analysis['RECOMMENDATION']
    elif period == 'all':
        handler.set_interval_as(Interval.INTERVAL_15_MINUTES)
        analysis = handler.get_analysis().summary
        analysis_final['15m'] = analysis['RECOMMENDATION']
        time.sleep(1)
        handler.set_interval_as(Interval.INTERVAL_1_HOUR)
        analysis = handler.get_analysis().summary
        analysis_final['1h'] = analysis['RECOMMENDATION']
        time.sleep(1)
        handler.set_interval_as(Interval.INTERVAL_4_HOURS)
        analysis = handler.get_analysis().summary
        analysis_final['4h'] = analysis['RECOMMENDATION']
        time.sleep(1)
        handler.set_interval_as(Interval.INTERVAL_1_DAY)
        analysis = handler.get_analysis().summary
        analysis_final['1d'] = analysis['RECOMMENDATION']
    return analysis_final

def sentiment_score(currency):
    #Dict from get_senti should be made to a list todo
    raw = get_senti(currency)
    final = list(raw.values())
    buy = list(final).count('BUY')
    sbuy = list(final).count('STRONG_BUY')
    sell = list(final).count('SELL')
    ssell = list(final).count('STRONG_SELL')
    total_score = buy + 3*sbuy + (-1*sell) + (-3*ssell)
    return total_score