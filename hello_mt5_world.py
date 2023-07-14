import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime
dia = datetime(2023, 7, 12)


mt5.initialize()
mt5.initialize()
d = mt5.terminal_info()
d.community_connection

dados = mt5.copy_ticks_from('PETR4', dia, 10, mt5.COPY_TICKS_ALL)
df = pd.DataFrame(dados)

print(df)

mt5.shutdown()