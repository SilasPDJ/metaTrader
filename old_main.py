import time

import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime
if not mt5.initialize():
    print('Not possible')
dia = datetime.today()
dias = 100
while True:
    data = time.time()
    # x = mt5.copy_rates_from('WIN$N', mt5.TIMEFRAME_M1, data, dias)
    x = mt5.copy_rates_from('WDO$', mt5.TIMEFRAME_M1, data, dias)
    x = pd.DataFrame(x)
    x['time'] = pd.to_datetime(x['time'], unit='s')
    p = x['close'].iloc[-1]
    print(p)
    time.sleep(2)

if __name__ == '__main__':
    pass
