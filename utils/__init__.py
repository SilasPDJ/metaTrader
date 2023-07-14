import MetaTrader5 as mt5
from typing import Union


def has_order_failed(result: mt5.OrderSendResult) -> bool:
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("2. order_send failed, retcode={}".format(result.retcode))
        # request the result as a dictionary and display it element by element
        result_dict = result._asdict()
        for field in result_dict.keys():
            print("   {}={}".format(field, result_dict[field]))
            # if this is a trading request structure, display it element by element as well
            if field == "request":
                traderequest_dict = result_dict[field]._asdict()
                for tradereq_filed in traderequest_dict:
                    print("       traderequest: {}={}".format(tradereq_filed, traderequest_dict[tradereq_filed]))
        print("shutdown() and quit")
        return True
    return False


def main_order_sender(symbol: str, _order_type: int,_lot: int, sl: int, tp: int, deviation=20) -> mt5.OrderSendResult:
    """
    :param symbol:
    :param _order_type:
    :param _lot: amount ot lots
    :param sl: stop loss
    :param tp: top gain

    :param deviation: Default: 20
    :return:
    """
    # pegando a ordem pelo tipo dela
    order_types_dict = {
        0: mt5.ORDER_TYPE_BUY,
        1: mt5.ORDER_TYPE_SELL,
        2: mt5.ORDER_TYPE_BUY_LIMIT,
        3: mt5.ORDER_TYPE_SELL_LIMIT,
        4: mt5.ORDER_TYPE_BUY_STOP,
        5: mt5.ORDER_TYPE_SELL_STOP,
        6: mt5.ORDER_TYPE_BUY_STOP_LIMIT,
        7: mt5.ORDER_TYPE_SELL_STOP_LIMIT,
        8: mt5.ORDER_TYPE_CLOSE_BY
    }
    assert 0 < _order_type < 8, "Invalid `_order_type: int` value"

    # prepare the sell/buy request structure
    symbol_info = mt5.symbol_info(symbol)
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

    # Declarando variaveis principais
    order_type = order_types_dict[_order_type]
    lot = symbol_info.volume_min * _lot
    point = mt5.symbol_info(symbol).point
    price = mt5.symbol_info_tick(symbol).ask

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": price - sl * point,
        "tp": price + tp * point,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }

    # send a trading request
    result = mt5.order_send(request)
    # check the execution result
    return result