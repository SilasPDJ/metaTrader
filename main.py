import MetaTrader5 as mt5
import pandas as pd
from utils import TradingUtils
import time

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

while True:
    positions_symbols = [pos.symbol for pos in mt5.positions_get()]

    if not trading_obj.symbol in positions_symbols:
        trading_obj.dolar_version_compra_e_vende(mt5.TIMEFRAME_M5)

    # trade = trading_obj.main_order_sender(_order_type=0, _lot=1, sl=8, tp=8)
    time.sleep(1)

# while True

# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
