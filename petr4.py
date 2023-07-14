import json
import time
import MetaTrader5 as mt5

order = json.loads(
    '{ "status": "NEW",  "type": "BUY",  "ticker": "PETR4",  "take_profit": "1.0820987897891143",  "stop_loss": "1.0819768153163283" }')

# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ", mt5.__author__)
print("MetaTrader5 package version: ", mt5.__version__)

# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# prepare the request structure
symbol = order['ticker']
order_type = mt5.ORDER_TYPE_BUY if order['ticker'] == 'BUY' else mt5.ORDER_TYPE_SELL
symbol_info = mt5.symbol_info(symbol)
tp = order['take_profit']
sl = order['stop_loss']

if symbol_info is None:
    print(symbol, "not found, can not call order_check()")
    mt5.shutdown()
    quit()

# if the symbol is unavailable in MarketWatch, add it
if not symbol_info.visible:
    print(symbol, "is not visible, trying to switch on")
    if not mt5.symbol_select(symbol, True):
        print("symbol_select({}}) failed, exit", symbol)
        mt5.shutdown()
        quit()

# prepare the order
price = mt5.symbol_info_tick(symbol).ask
deviation = 20
request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbol,
    "volume": symbol_info.volume_min,
    "type": order_type,
    "price": price,
    # "sl": sl,
    # "tp": tp,
    "deviation": deviation,
    "magic": 234000,
    "comment": "LUCRUM BOT",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_RETURN,
}

# send a trading request
result = mt5.order_send(request)
# check the execution result
print("[i] order_send(): by {} {} lots at {} with deviation={} points".format(symbol, 100, price, deviation))
if result.retcode != mt5.TRADE_RETCODE_DONE:
    print("[x] order_send failed, retcode={}".format(result.retcode))
    # request the result as a dictionary and display it element by element
    result_dict = result._asdict()
    for field in result_dict.keys():
        print("{}={}".format(field, result_dict[field]))
        # if this is a trading request structure, display it element by element as well
        if field == "request":
            traderequest_dict = result_dict[field]._asdict()
            for tradereq_filed in traderequest_dict:
                print("       traderequest: {}={}".format(tradereq_filed, traderequest_dict[tradereq_filed]))
    print("shutdown() and quit")
    mt5.shutdown()
    quit()
print("[i] order_send done, ", result)
print("[i] opened position with POSITION_TICKET={}".format(result.order))
