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
        # preparando a entrada
        _menor_tempo = out_ticks['time'].dt.floor('Min') >= tempo.floor('Min')
        _maior_tempo = out_ticks['time'].dt.floor('Min') < rates_5minutes.index[e + 1].floor('Min')

        ticks = out_ticks.loc[_menor_tempo & _maior_tempo]
        # é compra somente

        esta_comprado = False
        esta_vendido = False

        if e_compra:
            for cont, enter_tick in ticks.iterrows():
                if enter_tick.bid - abertura >= diferenca_abertura_fechamento and len(compras_entradas['price']) == len(
                        compras_saidas['price']):
                    # minha compra vai ser o tick.ask, pq é e_compra, mas é só um simulador

                    compras_entradas['price'].append(enter_tick.ask)
                    compras_entradas['horas'].append(enter_tick.time)
                    compras_entradas['stop_loss'].append(enter_tick.ask - 4.5)
                    compras_entradas['top_gain'].append(enter_tick.ask + 4)
                    # entrando
                    print('Entrada')
                    esta_comprado = True

                # achou a compra breaka, refatorar
                if esta_comprado:
                    for inner_cont, exit_tick in list(out_ticks.iterrows())[cont:]:
                        # print(exit_tick)
                        # indo somente uma posição por vez, price é uma key aleatória
                        # Sinal que está posicionado
                        # qual tick vai bater primeiro, do stop ou do gain?

                        # pegando sempre a última entrada
                        stopou = exit_tick.bid <= compras_entradas['stop_loss'][-1]
                        lucrou = exit_tick.ask >= compras_entradas['top_gain'][-1]
                        # print('exit_tick.ask: ', exit_tick.ask, 'top_gain:', compras_entradas['top_gain'][-1], f'entrada: {compras_entradas["price"][-1]}')

                        if stopou:
                            print('Bateu o loss primeiro')
                        if lucrou:
                            print('LUCROOOO !!!! ')
                        if stopou or lucrou:
                            print(f'\033[1;32mEntrou em {compras_entradas["price"][-1]}, Saiu em {exit_tick.bid}. COMPRA\033[1;32m')
                            # certifica que tenha uma entrada a mais antes de appendar...

                            compras_saidas['price'].append(exit_tick.ask)
                            compras_saidas['horas'].append(exit_tick.time)
                            same_entrada_indx = len(compras_saidas['price']) - 1

                            compras_saidas['resultado_pontos'].append(
                                (exit_tick.ask - compras_entradas['price'][same_entrada_indx]))
                            print()
                            break
                        break

df_compras_final = pd.DataFrame(ORDENS_WDO['compras'])
# df_compras_final['Lucro'] = compras_saidas['resultado_pontos'] * 10
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
