from binance import Client
from api_keys import api_key, secret
from stc_ema_adx import run_trading_1
import threading
import time

client = Client(api_key=api_key, api_secret=secret)

symbols = ['DOGEBUSD', 'BNBBUSD', 'ETHBUSD', 'SOLBUSD', 'BTCBUSD']

def get_symbol_qty(symbol):
    symbol_price = client.get_symbol_ticker(symbol=symbol)
    qty = 12 / float(symbol_price['price'])
    return qty

doge_qty = round(get_symbol_qty('DOGEBUSD'))
bnb_qty = round(get_symbol_qty('BNBBUSD'), 3)
eth_qty = round(get_symbol_qty('ETHBUSD'), 4)
sol_qty = round(get_symbol_qty('SOLBUSD'), 2)
btc_qty = round(get_symbol_qty('BTCBUSD'), 4)

thread_DOGE_2 = threading.Thread(target=run_trading_1, args=('DOGEBUSD', '15m', '10000', doge_qty))
thread_BNB_2 = threading.Thread(target=run_trading_1, args=('BNBBUSD', '15m', '10000', bnb_qty))
thread_ETH_2 = threading.Thread(target=run_trading_1, args=('ETHBUSD', '15m', '10000', eth_qty))
thread_SOL_2 = threading.Thread(target=run_trading_1, args=('SOLBUSD', '15m', '10000', sol_qty))
thread_BTC_2 = threading.Thread(target=run_trading_1, args=('BTCBUSD', '15m', '10000', btc_qty))

thread_DOGE_2.start()
time.sleep(2)
thread_BNB_2.start()
time.sleep(2)
thread_ETH_2.start()
time.sleep(2)
thread_SOL_2.start()
time.sleep(2)
thread_BTC_2.start()



