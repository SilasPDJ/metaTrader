import MetaTrader5 as mt5

if not mt5.initialize():
    print('Not Possible')

symbols = ['WIN$N', 'WDO$', 'VGFH11', 'VALE3', 'CASH3', 'VAMO3', 'ITUB4', 'SOMA3', 'VAMO3', 'BPAC11']

for symbol in symbols:
    mt5.symbol_select(symbol, True)
