import MetaTrader5 as mt5


# Verificar se a conexão foi bem-sucedida
if not mt5.initialize():
    print("Não foi possível conectar-se ao MetaTrader 5.")
    mt5.shutdown()
    quit()

# Obter informações sobre a conta
account_info = mt5.account_info()

# Verificar se as informações da conta foram obtidas com sucesso
if account_info is None:
    print("Não foi possível obter informações da conta.")
    mt5.shutdown()
    quit()

# Imprimir o saldo da conta
print("Saldo da conta:", account_info.balance)

# Desconectar-se da plataforma MetaTrader 5
mt5.shutdown()
