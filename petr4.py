import MetaTrader5 as mt5
from utils import main_order_sender

# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ", mt5.__author__)
print("MetaTrader5 package version: ", mt5.__version__)

# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# comprinha_de_petro =  main_order_sender(symbol='PETR4', _order_type=0, _lot=1, sl=10, tp=10)
# indice =  main_order_sender(symbol='WINQ23', _order_type=0, _lot=1, sl=100, tp=100)
indice = main_order_sender(symbol='WDOQ23', _order_type=0, _lot=1, sl=8, tp=8)

# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
