import time
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime
import datetime as dt
from typing import Union


class TradingDolar:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.yesterday = datetime.today() + dt.timedelta(-4)
        if not self.has_position():
            pass



    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, symbol: str):
        self._symbol = symbol

    def has_position(self) -> bool:
        return self.symbol in [pos.symbol for pos in mt5.positions_get()]

    def dolar_version_compra_e_vende(self, timeframe, diferenca_abertura_fechamento: float, count_df: int = 10) -> bool:
        positions_symbols = [pos.symbol for pos in mt5.positions_get()]
        # assert diferenca_abertura_fechamento > 0.5
        symbol_info = mt5.symbol_info(self.symbol)
        symbol_info_tick = mt5.symbol_info_tick(self.symbol)
        rates = mt5.copy_rates_from(self.symbol, timeframe, time.time(), count_df)

        # settando df
        df = pd.DataFrame(rates)
        df['time'] = df['time'].apply(datetime.fromtimestamp)
        # carteira_closes.set_index(timestamps, inplace=True)

        # Se a ordem já estiver aberta, não executa
        if self.symbol in positions_symbols:
            print('Orderm já aberta')
            return False

        tempo, abertura, high, low, close, tick_volume, spread,real_volume = df.iloc[-1]
        print(f'abertura: {abertura}\n'
              f'Fechamento: {close}\n'
              f'{abertura-close}')


        if close > abertura:
            # É compra
            if close - abertura >= diferenca_abertura_fechamento:

                price = self._get_price(high, low)
                self.main_order_sender(_order_type=0, _lot=1, price=price, sl=diferenca_abertura_fechamento, tp=diferenca_abertura_fechamento)
                return True

            return False
        elif close < abertura:
            # É venda
            if abertura - close >= diferenca_abertura_fechamento:
                price = self._get_price(high, low)
                self.main_order_sender(_order_type=1, _lot=1, price=price, sl=diferenca_abertura_fechamento, tp=diferenca_abertura_fechamento)
                return True
            return False

    def _get_price(self, high: float, low: float) -> float:
        valor = (high + low) / 2
        if valor % 1 != 0.5:
            return float(round(valor))
        else:
            return valor

    def main_order_sender(self, _order_type: int, _lot: int, price:float,sl: float, tp: float, deviation=20) -> mt5.OrderSendResult:
        """
        :param _order_type:
        :param _lot: amount ot lots
        :param price:
        :param sl: stop loss in cents or points
        :param tp: take profit in cents or points

        :param deviation: Default: 20
        :return:
        """
        # pegando a ordem pelo tipo dela
        order_types_dict = {
            0: "mt5.ORDER_TYPE_BUY",
            1: "mt5.ORDER_TYPE_SELL",
            2: "mt5.ORDER_TYPE_BUY_LIMIT",
            3: "mt5.ORDER_TYPE_SELL_LIMIT",
            4: "mt5.ORDER_TYPE_BUY_STOP",
            5: "mt5.ORDER_TYPE_SELL_STOP",
            6: "mt5.ORDER_TYPE_BUY_STOP_LIMIT",
            7: "mt5.ORDER_TYPE_SELL_STOP_LIMIT",
            8: "mt5.ORDER_TYPE_CLOSE_BY"
        }
        assert 0 <= _order_type <= 8, "Invalid `_order_type: int` value"

        # prepare the sell/buy request structure
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            print(self.symbol, "not found, can not call order_check()")
            mt5.shutdown()
            quit()

        # if the symbol is unavailable in MarketWatch, add it
        if not symbol_info.visible:
            print(self.symbol, "is not visible, trying to switch on")
            if not mt5.symbol_select(self.symbol, True):
                print("symbol_select({}}) failed, exit", self.symbol)
                mt5.shutdown()
                quit()

        order_type_str = order_types_dict[_order_type]
        lot = symbol_info.volume_min * _lot
        trade_tick_size = mt5.symbol_info(self.symbol).trade_tick_size
        # mt5.symbol_info_tick._as_dict().keys() = time, bid, ask, last, volume, time_msc, flags, volume_real

        if trade_tick_size == 0.01 or trade_tick_size == 0.5:
            # Ordem é do tipo buy
            if _order_type % 2 == 0:
                stop_loss_formula = price - sl * trade_tick_size
                take_profit_formula = price + tp * trade_tick_size
            else:
                # ordem do tipo sell
                stop_loss_formula = price + sl * trade_tick_size
                take_profit_formula = price - tp * trade_tick_size

        elif trade_tick_size == 5:
            # Ordem é do tipo buy
            if _order_type % 2 == 0:
                take_profit_formula = price + tp
                stop_loss_formula = price - sl
            else:
                # ordem do tipo sell
                stop_loss_formula = price + sl
                take_profit_formula = price - tp
        else:
            print(f'trade tick_size = {trade_tick_size}')
            raise ValueError('Ativo não identificado ainda')

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": lot,
            "type": _order_type,
            "price": price,
            "sl": stop_loss_formula,
            "tp": take_profit_formula,
            "deviation": deviation,
            "magic": 234000,
            "comment": "python script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
        df_result = pd.DataFrame(data=request.values(), index=request.keys()).T

        # send a trading request
        result = mt5.order_send(request)

        # check the execution result
        # if self._has_order_failed(result):
            # mt5.shutdown()
            # quit()
            # pass

        print(f'symbol: {self.symbol}')
        print(f'order type: {order_type_str}\n'
              f'take profit: {take_profit_formula}, ({tp} ticks)\n'
              f'stop loss: {stop_loss_formula}, ({sl} ticks)\n'
              f'')

        return result

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

if __name__ == '__main__':
    pass