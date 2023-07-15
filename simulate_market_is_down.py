import MetaTrader5 as mt5
import pandas as pd
import datetime as dt
from utils import TradingUtils
import time
import cufflinks as cf
cf.set_config_file(offline=True)
# pip install jupyter
# jupyter notebook
# http://127.0.0.1:8888/notebooks/Untitled.ipynb?kernel_name=python3


# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ", mt5.__author__)
print("MetaTrader5 package version: ", mt5.__version__)

# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# comprinha_de_petro =  main_order_sender(symbol='PETR4', _order_type=0, _lot=1, sl=10, tp=10)
# indice =  main_order_sender(symbol='WINQ23', _order_type=0, _lot=1, sl=100, tp=100)

trading_obj = TradingUtils('WDOQ23')

rates_5minutes = trading_obj.get_rates_previous_day(mt5.TIMEFRAME_M5)
rates_1minute = trading_obj.get_rates_previous_day(mt5.TIMEFRAME_M1)


out_ticks = trading_obj.get_ticks_previous_day()

df = rates_5minutes
# Ok, eu ja tenho os rates, agora é só eu verificaar se vai satisfazer minha condição
# TODO stop tem que ser na minima do candle de entrada

compra = df['open'] < df['close']
venda = df['open'] > df['close']

df_compra = df[compra]
df_venda = df[venda]

maiorq7_compras = df_compra.loc[df_compra['close'] - df_compra['open'] >= 7]
maiorq7_vendas = df_venda.loc[df_venda['open'] - df_venda['close'] >= 7]


def get_ticks_in_candle_price(_tick: pd.DataFrame) -> pd.DataFrame:
    bid_in_price= (_tick['bid'] >= candle['low']) & (_tick['bid'] <= candle['high'])
    ask_in_price = (_tick['ask'] >= candle['low']) & (_tick['ask'] <= candle['high'])

    return _tick.loc[bid_in_price & ask_in_price]

for e, (tempo, candle) in enumerate(rates_5minutes.iterrows()):
    _menor_tempo =out_ticks['time'].dt.floor('Min') >= tempo.floor('Min')
    _maior_tempo = out_ticks['time'].dt.floor('Min') < rates_5minutes.index[e+1].floor('Min')

    ticks = get_ticks_in_candle_price(out_ticks.loc[_menor_tempo & _maior_tempo])
    print(candle, ticks)



    print(candle)
    print()





# maiorq7_vendas[['open', 'high', 'low', 'close']].iplot(kind='candle')
# maiorq7_compras[['open', 'high', 'low', 'close']].iplot(kind='candle')




while True:
    positions_symbols = [pos.symbol for pos in mt5.positions_get()]

    if not trading_obj.symbol in positions_symbols:
        trading_obj.dolar_version_compra_e_vende(mt5.TIMEFRAME_M5)

    # trade = trading_obj.main_order_sender(_order_type=0, _lot=1, sl=8, tp=8)
    time.sleep(1)

# while True

# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
