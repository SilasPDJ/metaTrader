import os, sys, argparse
import pandas as pd
import backtrader as bt
from strategies.GoldenCross import GoldenCross
from strategies.BuyHold import BuyHold

cerebro = bt.Cerebro()
cerebro.broker.set_cash(100000)

spy_prices = pd.read_csv('data/SPY.csv', index_col='Date', parse_dates=True)

feed = bt.feeds.PandasData(dataname=spy_prices)
cerebro.adddata(feed)

cerebro.addstrategy(GoldenCross)
cerebro.run()
cerebro.plot()
