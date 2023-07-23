import backtrader as bt
import datetime
import pandas as pd

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt


# Create a Stratey
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datahlow = self.datas[0].low
        self.datahvolume = self.datas[0].volume

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] > self.dataclose[-1]:
                # current close less than previous close
                # previous close less than the previous close

                # BUY, BUY, BUY!!! (with default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                price = self.dataclose[0]
                stopprice = self.datahlow[-1]  # Stop and Tgt prices should be set from the executed price
                limitprice = price + ((price - stopprice) / 2)  # not the submitted price

                self.buy_bracket(price=price, stopprice=stopprice, limitprice=limitprice,
                                      exectype=bt.Order.Market)
                self.log(f'Buy at {price}, Stop sell at {stopprice}, Tgt sell at {limitprice}')

        else:

            # Already in the market ... we might sell
            if len(self) >= (self.bar_executed + 5):
                pass


if __name__ == '__main__':
    cerebro = bt.Cerebro()

    df = pd.read_csv('historical_data_v2.csv')
    # df.set_index('time', inplace=True)
    df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%d %H:%M:%S')

    df.index = df['time']
    data = bt.feeds.PandasData(dataname=df, name='WDO_5M')

    cerebro.adddata(data)
    cerebro.broker.set_cash(10000)

    cerebro.addstrategy(TestStrategy)
    print('Starting Portifolio Value: %.2f' % cerebro.broker.get_value())

    cerebro.run()
    print('Final Portifolio Value: %.2f' % cerebro.broker.get_value())
    print()
