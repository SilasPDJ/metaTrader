import time
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime
import datetime as dt
from typing import Union


class TradingUtils:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.yesterday = datetime.today() + dt.timedelta(-4)

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, symbol: str):
        self._symbol = symbol

    def _get_price(self, high: float, low: float) -> float:
        valor = (high + low) / 2
        if valor % 1 != 0.5:
            return float(round(valor))
        else:
            return valor

    @staticmethod
    def _has_order_failed(result: mt5.OrderSendResult) -> bool:
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


class PreviousDay(TradingUtils):
    def __init__(self, symbol: str):
        super().__init__(symbol)

    def get_ticks_previous_day(self):
        date_from = pd.Timestamp(self.yesterday).replace(hour=0, minute=0, second=0)
        date_to = pd.Timestamp(self.yesterday).replace(hour=23, minute=59, second=59)

        ticks = mt5.copy_ticks_range(self.symbol, date_from, date_to, mt5.COPY_TICKS_INFO)

        # Filtrar apenas as alterações do Ask e Bid
        bid_flags = ticks['flags'] & mt5.TICK_FLAG_BID
        ask_flags = ticks['flags'] & mt5.TICK_FLAG_ASK
        # newticks = pd.DataFrame(ticks)
        ask_bid_ticks = pd.DataFrame(ticks)[['time', 'bid', 'ask']].loc[(bid_flags != 0) | (ask_flags != 0)]
        ask_bid_ticks['time'] = ask_bid_ticks['time'].apply(dt.datetime.fromtimestamp)

        return ask_bid_ticks

    def get_rates_previous_day(self, timeframe) -> pd.DataFrame:
        # rates = mt5.copy_rates_from(self.symbol, timeframe, yesterday, 120)
        rates = mt5.copy_rates_from(self.symbol, timeframe, self.yesterday + dt.timedelta(1), 600)
        df = pd.DataFrame(rates)
        df['time'] = df['time'].apply(datetime.fromtimestamp)
        # pegar o dia máximo
        df = df.loc[df['time'].dt.date == self.yesterday.date()]
        df.set_index('time', inplace=True)
        return df

