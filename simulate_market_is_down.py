import MetaTrader5 as mt5
import pandas as pd
import datetime as dt
from utils import TradingUtils
import time
import cufflinks as cf

cf.set_config_file(offline=True)
# pip install jupyter
# jupyter notebook
# http://127.0.0.1:8888/notebooks/Untitled.ipynb?kernel_name=python3


# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ", mt5.__author__)
print("MetaTrader5 package version: ", mt5.__version__)

# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# comprinha_de_petro =  main_order_sender(symbol='PETR4', _order_type=0, _lot=1, sl=10, tp=10)
# indice =  main_order_sender(symbol='WINQ23', _order_type=0, _lot=1, sl=100, tp=100)

trading_obj = TradingUtils('WDOQ23')

rates_5minutes = trading_obj.get_rates_previous_day(mt5.TIMEFRAME_M5)
rates_1minute = trading_obj.get_rates_previous_day(mt5.TIMEFRAME_M1)

out_ticks = trading_obj.get_ticks_previous_day()

df = rates_5minutes
# Ok, eu ja tenho os rates, agora é só eu verificaar se vai satisfazer minha condição
# TODO stop tem que ser na minima do candle de entrada

compra = df['open'] < df['close']
venda = df['open'] > df['close']

df_compra = df[compra]
df_venda = df[venda]

maiorq7_compras = df_compra.loc[df_compra['close'] - df_compra['open'] >= 7]
maiorq7_vendas = df_venda.loc[df_venda['open'] - df_venda['close'] >= 7]

diferenca_abertura_fechamento = 7


def get_ticks_in_candle_price(_tick: pd.DataFrame) -> pd.DataFrame:
    bid_in_price = (_tick['bid'] >= candle['low']) & (_tick['bid'] <= candle['high'])
    ask_in_price = (_tick['ask'] >= candle['low']) & (_tick['ask'] <= candle['high'])

    return _tick.loc[bid_in_price & ask_in_price]


ORDENS_WDO = {
    'compras': {
        'entradas': {
            'horas': [],
            'price': [],
            'stop_loss': [],
            'top_gain': [],
        },
        'saidas': {
            'horas': [],
            'price': [],
            'resultado_pontos': [],
        }
    },
    'vendas': {
        'entradas': {
            'horas': [],
            'price': [],
            'stop_loss': [],
            'top_gain': [],
        },
        'saidas': {
            'horas': [],
            'price': [],
            'resultado_pontos': [],
        }
    }
}
compras_entradas = ORDENS_WDO['compras']['entradas']
compras_saidas = ORDENS_WDO['compras']['saidas']

vendas_entradas = ORDENS_WDO['vendas']['entradas']
vendas_saidas = ORDENS_WDO['vendas']['saidas']

for e, (tempo, candle) in enumerate(rates_5minutes.iterrows()):
    # só vou checar os ticks se satisfazer minha condição...
    abertura, high, low, close, tick_volume, spread, real_volume = candle

    e_compra = e_venda = False
    if close > abertura:
        # É compra
        if close - abertura >= diferenca_abertura_fechamento:
            # self.main_order_sender(_order_type=0, _lot=1, sl=8, tp=8)
            e_compra = True
    elif close < abertura:
        # É venda
        if abertura - close >= diferenca_abertura_fechamento:
            # self.main_order_sender(_order_type=1, _lot=1, sl=8, tp=8)

            e_venda = True

    # entao se for uma compra ou uma venda, eu vou pegar o exato momento em que deu a compra
    if e_compra or e_venda:
        _menor_tempo = out_ticks['time'].dt.floor('Min') >= tempo.floor('Min')
        _maior_tempo = out_ticks['time'].dt.floor('Min') < rates_5minutes.index[e + 1].floor('Min')

        ticks = get_ticks_in_candle_price(out_ticks.loc[_menor_tempo & _maior_tempo])

        # é compra somente
        if e_compra:
            for cont, tick in ticks.iterrows():
                if tick.bid - abertura == diferenca_abertura_fechamento and len(compras_entradas['price']) == len(compras_saidas['price']):
                    # minha compra vai ser o tick.ask, pq é e_compra, mas é só um simulador

                    compras_entradas['price'].append(tick.ask)
                    compras_entradas['horas'].append(tick.time)
                    compras_entradas['stop_loss'].append(tick.ask - 4.5)
                    compras_entradas['top_gain'].append(tick.ask + 4)

                    df_compras_entradas = pd.DataFrame(compras_entradas)
                    # entrando
                    print('Entrada')

                # indo somente uma posição por vez, price é uma key aleatória
                if len(compras_entradas['price']) > len(compras_saidas['price']):
                    # Sinal que está posicionado
                    # qual tick vai bater primeiro, do stop ou do gain?

                    # pegando sempre a última entrada
                    stopou = tick.ask == compras_entradas['stop_loss'][-1]
                    lucrou = tick.ask == compras_entradas['top_gain'][-1]

                    if stopou or lucrou and  len(compras_entradas) > len(compras_saidas):
                        # certifica que tenha uma entrada a mais antes de appendar...

                        compras_saidas['price'].append(tick.ask)
                        compras_saidas['horas'].append(tick.time)
                        same_entrada_indx = len(compras_saidas['price']) - 1

                        compras_saidas['resultado_pontos'].append((tick.ask - compras_entradas['price'][same_entrada_indx]))
                        print(compras_saidas)
                        print()
                    if stopou:
                        print('Bateu o loss primeiro')
                    if lucrou:
                        print('LUCROOOO !!!! ')


        print(candle, ticks)
df_compras_final = pd.DataFrame(ORDENS_WDO['compras'])
print()

# maiorq7_vendas[['open', 'high', 'low', 'close']].iplot(kind='candle')
# maiorq7_compras[['open', 'high', 'low', 'close']].iplot(kind='candle')


while True:
    positions_symbols = [pos.symbol for pos in mt5.positions_get()]

    if not trading_obj.symbol in positions_symbols:
        trading_obj.dolar_version_compra_e_vende(mt5.TIMEFRAME_M5)

    # trade = trading_obj.main_order_sender(_order_type=0, _lot=1, sl=8, tp=8)
    time.sleep(1)

# while True
maiorq7_compras[['open', 'high', 'low', 'close']].iplot(kind='candle')

# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
