import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, date, time, timedelta

def _get_last_market_days(market='BMF', days_amount_before_today=30) -> list[datetime.date]:
    """
    :param market: dict_keys(['ASX', 'BMF', 'B3', 'CFE', 'CBOE_Futures', 'CBOE_Equity_Options', 'CBOE_Index_Options', 'CME_Equity', 'CBOT_Equity', 'CME_Agriculture', 'CBOT_Agriculture', 'COMEX_Agriculture', 'NYMEX_Agriculture', 'CME_Rate', 'CBOT_Rate', 'CME_InterestRate', 'CBOT_InterestRate', 'CME_Bond', 'CBOT_Bond', 'CMEGlobex_Livestock', 'CMEGlobex_Live_Cattle', 'CMEGlobex_Feeder_Cattle', 'CMEGlobex_Lean_Hog', 'CMEGlobex_Port_Cutout', 'CMEGlobex_FX', 'CME_FX', 'CME_Currency', 'CMEGlobex_EnergyAndMetals', 'CMEGlobex_Energy', 'CMEGlobex_CrudeAndRefined', 'CMEGlobex_NYHarbor', 'CMEGlobex_HO', 'HO', 'CMEGlobex_Crude', 'CMEGlobex_CL', 'CL', 'CMEGlobex_Gas', 'CMEGlobex_RB', 'RB', 'CMEGlobex_MicroCrude', 'CMEGlobex_MCL', 'MCL', 'CMEGlobex_NatGas', 'CMEGlobex_NG', 'NG', 'CMEGlobex_Dutch_NatGas', 'CMEGlobex_TTF', 'TTF', 'CMEGlobex_LastDay_NatGas', 'CMEGlobex_NN', 'NN', 'CMEGlobex_CarbonOffset', 'CMEGlobex_CGO', 'CGO', 'C-GEO', 'CMEGlobex_NGO', 'NGO', 'CMEGlobex_GEO', 'GEO', 'CMEGlobex_Metals', 'CMEGlobex_PreciousMetals', 'CMEGlobex_Gold', 'CMEGlobex_GC', 'GC', 'CMEGlobex_SilverCMEGlobex_SI', 'SI', 'CMEGlobex_Platinum', 'CMEGlobex_PL', 'PL', 'CMEGlobex_BaseMetals', 'CMEGlobex_Copper', 'CMEGlobex_HG', 'HG', 'CMEGlobex_Aluminum', 'CMEGlobex_ALI', 'ALI', 'CMEGlobex_QC', 'QC', 'CMEGlobex_FerrousMetals', 'CMEGlobex_HRC', 'HRC', 'CMEGlobex_BUS', 'BUS', 'CMEGlobex_TIO', 'TIO', 'CME Globex Equity', 'CME Globex Fixed Income', 'CME Globex Interest Rate Products', 'EUREX', 'HKEX', 'ICE', 'ICEUS', 'NYFE', 'NYSE', 'stock', 'NASDAQ', 'BATS', 'DJIA', 'DOW', 'IEX', 'Investors_Exchange', 'JPX', 'LSE', 'OSE', 'SIFMAUS', 'SIFMA_US', 'Capital_Markets_US', 'Financial_Markets_US', 'Bond_Markets_US', 'SIFMAUK', 'SIFMA_UK', 'Capital_Markets_UK', 'Financial_Markets_UK', 'Bond_Markets_UK', 'SIFMAJP', 'SIFMA_JP', 'Capital_Markets_JP', 'Financial_Markets_JP', 'Bond_Markets_JP', 'SIX', 'SSE', 'TSX', 'TSXV', 'BSE', 'NSE', 'TASE', 'TradingCalendar', 'AIXK', 'ASEX', 'BVMF', 'CMES', 'IEPA', 'XAMS', 'XASX', 'XBKK', 'XBOG', 'XBOM', 'XBRU', 'XBSE', 'XBUD', 'XBUE', 'XCBF', 'XCSE', 'XDUB', 'XFRA', 'XETR', 'XHEL', 'XHKG', 'XICE', 'XIDX', 'XIST', 'XJSE', 'XKAR', 'XKLS', 'XKRX', 'XLIM', 'XLIS', 'XLON', 'XMAD', 'XMEX', 'XMIL', 'XMOS', 'XNYS', 'XNZE', 'XOSL', 'XPAR', 'XPHS', 'XPRA', 'XSAU', 'XSES', 'XSGO', 'XSHG', 'XSTO', 'XSWX', 'XTAE', 'XTAI', 'XTKS', 'XTSE', 'XWAR', 'XWBO', 'us_futures', '24/7', '24/5'])
    :param days_amount_before_today: count past today
    :return:
    """
    from pandas_market_calendars import get_calendar

    brazil_calendar = get_calendar(market)

    business_days = brazil_calendar.valid_days(datetime.today() - timedelta(days_amount_before_today),
                                               datetime.today())

    business_days = [day.date() for day in business_days]
    return [datetime.combine(day, time.min) for day in business_days]


# Initialize MetaTrader 5 connection
mt5.initialize()

# Set the symbol and timeframe you want to export
symbol = 'WDOQ23'
timeframe = mt5.TIMEFRAME_M5  # 1-minute data, you can change this

# Request historical data
# bars = mt5.copy_rates_from_pos(symbol, timeframe, 0, 1000)  # Get 1000 bars

last_market_days = _get_last_market_days()
bars = mt5.copy_rates_range(symbol, timeframe, last_market_days[0], last_market_days[-1])
# Convert the data to a pandas DataFrame
df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'tick_volume', 'spread', 'real_volume'])
df['time'] = pd.to_datetime(df['time'], unit='s')
df.set_index('time', inplace=True)

# Save the DataFrame to a CSV file
df.to_csv('historical_data_v2.csv')

# Deinitialize MetaTrader 5 connection
mt5.shutdown()
