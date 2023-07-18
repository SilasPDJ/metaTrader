import pandas as pd
import backtrader as bt
import matplotlib.pyplot as plt

class MyStrategy(bt.Strategy):
    params = (
        ('quantidade_pontos', 2),  # Valor padrão para quantidade_pontos
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open  # Preço de abertura do candle
        self.order = None
        self.price = None
        self.stop_loss = None
        self.take_profit = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.price = order.executed.price
                self.stop_loss = self.price - self.p.quantidade_pontos
                self.take_profit = self.price + self.p.quantidade_pontos
                print(f"Buy Order executed: Price: {self.price:.2f}, Stop Loss: {self.stop_loss:.2f}, Take Profit: {self.take_profit:.2f}")
            elif order.issell():
                self.price = order.executed.price
                self.stop_loss = self.price + self.p.quantidade_pontos
                self.take_profit = self.price - self.p.quantidade_pontos
                print(f"Sell Order executed: Price: {self.price:.2f}, Stop Loss: {self.stop_loss:.2f}, Take Profit: {self.take_profit:.2f}")


    def next(self):
        if self.order:
            return
        # Verifica se a distância de abertura para fechamento é igual a quantidade_pontos para operações de compra
        distance_buy = self.dataclose[0] - self.dataopen[0]
        # print(f"Buy Distance: {distance_buy:.2f}, Quantity of Points: {self.p.quantidade_pontos:.2f}")

        if distance_buy*-1 >= self.p.quantidade_pontos:
            print("Buy Condition met. Placing orders.")
            # Adiciona stop loss e take profit
            self.buy(exectype=bt.Order.Stop, price=self.stop_loss)
            self.buy(exectype=bt.Order.Limit, price=self.take_profit)

        # Verifica se a distância de abertura para fechamento é igual a quantidade_pontos para operações de venda
        distance_sell = self.dataopen[0] - self.dataclose[0]
        # print(f"Sell Distance: {distance_sell:.2f}, Quantity of Points: {self.p.quantidade_pontos:.2f}")

        if distance_sell*-1 >= self.p.quantidade_pontos:
            print("Sell Condition met. Placing orders.")
            # Adiciona stop loss e take profit
            self.sell(exectype=bt.Order.Stop, price=self.stop_loss)
            self.sell(exectype=bt.Order.Limit, price=self.take_profit)

if __name__ == "__main__":
    cerebro = bt.Cerebro()

    # Load your historical data into a pandas DataFrame
    data = pd.read_csv('historical_data.csv', index_col='time', parse_dates=True)

    # Convert the DataFrame to a 'backtrader' data feed
    data_feed = bt.feeds.PandasData(dataname=data)

    cerebro.adddata(data_feed)
    cerebro.addstrategy(MyStrategy, quantidade_pontos=4)  # Passa a quantidade_pontos como parâmetro

    # Set your starting cash amount
    cerebro.broker.set_cash(10000)

    # Add any other configurations (e.g., commission, slippage, etc.)

    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())

    # Run the backtest
    cerebro.run()

    print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())
