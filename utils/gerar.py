import MetaTrader5 as mt5
import pandas as pd

# Initialize MetaTrader 5 connection
mt5.initialize()

# Set the symbol and timeframe you want to export
symbol = 'WDOQ23'
timeframe = mt5.TIMEFRAME_M1  # 1-minute data, you can change this

# Request historical data
bars = mt5.copy_rates_from_pos(symbol, timeframe, 0, 1000)  # Get 1000 bars

# Convert the data to a pandas DataFrame
df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'tick_volume', 'spread', 'real_volume'])
df['time'] = pd.to_datetime(df['time'], unit='s')
df.set_index('time', inplace=True)

# Save the DataFrame to a CSV file
df.to_csv('historical_data.csv')

# Deinitialize MetaTrader 5 connection
mt5.shutdown()
