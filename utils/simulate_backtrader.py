import backtrader as bt
import pandas as pd
from utils import TradingUtils
import MetaTrader5 as mt5


class TestStrategy(bt.Strategy):
    def __init__(self):
        self.trading_obj = TradingUtils('WDOQ23')

    def next(self):
        # Chamar sua estratégia para compra ou venda aqui
        self.trading_obj.dolar_version_compra_e_vende(
            timeframe=bt.TimeFrame.Minutes,
            diferenca_abertura_fechamento=4
        )

# Carregar dados históricos
trading_obj = TradingUtils('WDOQ23')
df_5minutes = trading_obj.get_rates_previous_day(mt5.TIMEFRAME_M5)
df_1minute = trading_obj.get_ticks_previous_day()

data = bt.feeds.PandasData(dataname=df_1minute)

# Criar cerebro (backtest engine)
cerebro = bt.Cerebro()

# Adicionar o feed de dados
cerebro.adddata(data)

# Adicionar a estratégia
cerebro.addstrategy(TestStrategy)

# Configurar o capital inicial
cerebro.broker.set_cash(10000)

# Configurar o tamanho do lote
cerebro.addsizer(bt.sizers.FixedSize, stake=1)

# Configurar a comissão
cerebro.broker.setcommission(commission=0.001)

# Rodar o backtest
cerebro.run()

# Obter os resultados
print('Valor Final:', cerebro.broker.getvalue())

# Plotar o gráfico
cerebro.plot()
