import time

import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime

dia = datetime.today()




if not mt5.initialize():
    print('Tivemos problemas')
    quit()

dias = 100
data = time.time()

carteira_closes = pd.DataFrame()

acoes = ['PETR4', 'ABEV3', 'B3SA3', 'CIEL3', 'COGN3',
         'ITUB4', 'ITSA4', 'VGHF11', 'WEGE3', 'VALE3']

for ativo in acoes:
    copied_rates = mt5.copy_rates_from(ativo, mt5.TIMEFRAME_W1, data, dias)
    carteira_closes[ativo] = copied_rates['close']
    if ativo == acoes[0]:
        # Convert the 'copied_rates' numpy array to a pandas DataFrame
        copied_rates_df = pd.DataFrame(copied_rates, columns=['time'])

        # Convert timestamps in 'copied_rates_df['time']' to datetime objects
        timestamps = copied_rates_df['time'].apply(datetime.fromtimestamp)

        # Set the index of 'carteira_closes' using the converted timestamps
        carteira_closes.set_index(timestamps, inplace=True)

print(carteira_closes)


if __name__ == '__main__':
    pass