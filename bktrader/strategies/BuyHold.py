import math
import backtrader as bt
import pandas as pd


class BuyHold(bt.Strategy):
    def next(self):

        if self.position.size == 0:
            size = int(self.broker.getcash() / self.data)
            self.buy(size=size)
