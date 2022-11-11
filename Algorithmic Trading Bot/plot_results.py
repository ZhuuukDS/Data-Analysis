import pandas as pd
import numpy as np
from binance import Client
from api_keys import api_key, secret
import matplotlib.pyplot as plt
import seaborn as sns
pd.set_option('display.max_columns', None)

client = Client(api_key=api_key, api_secret=secret)


def get_qty(symbol):
    symbol_price = client.get_symbol_ticker(symbol=symbol)
    qty = 12 / float(symbol_price['price'])
    return qty

doge_qty = round(get_qty('DOGEBUSD'))
bnb_qty = round(get_qty('BNBBUSD'), 3)
eth_qty = round(get_qty('ETHBUSD'), 4)
sol_qty = round(get_qty('SOLBUSD'), 2)
btc_qty = round(get_qty('BTCBUSD'), 4)


def get_res(symbol, qty):
    results = pd.read_csv('trading_strategy_1.csv')
    coin = results[results['symbol'] == symbol].fillna(0)
    coin['short_open'] = coin['short_open'].replace(to_replace=0, method='ffill')
    coin['long_open'] = coin['long_open'].replace(to_replace=0, method='ffill')
    coin['short_value'] = np.where(coin.short_close != 0, qty * sum([coin.short_open, coin.short_close]), 0)
    coin['long_value'] = np.where(coin.long_close != 0, btc_qty * sum([coin.long_open, coin.long_close]), 0)
    coin['values'] = coin['short_value'] + coin['long_value']
    coin['res'] = coin['values'].cumsum()
    coin_result = coin[coin['values'] != 0][['time', 'res']]
    coin_result = pd.concat([pd.DataFrame({'time': '2022-11-09 00:00:00', 'res': 0}, index=[0]), coin_result])
    coin_result = coin_result.set_index(coin_result.time).drop(['time'], axis=1)
    coin_result.index = pd.to_datetime(coin_result.index)
    return coin_result

print(get_res('BTCBUSD', btc_qty))
print(get_res('BNBBUSD', bnb_qty))
print(get_res('DOGEBUSD', doge_qty))
print(get_res('ETHBUSD', eth_qty))
print(get_res('SOLBUSD', sol_qty))


sns.lineplot(data=get_res('BTCBUSD', btc_qty), x='time', y='res', color='orange')
sns.lineplot(data=get_res('BNBBUSD', bnb_qty), x='time', y='res', color='blue')
sns.lineplot(data=get_res('DOGEBUSD', doge_qty), x='time', y='res', color='green')
sns.lineplot(data=get_res('ETHBUSD', eth_qty), x='time', y='res', color='purple')
sns.lineplot(data=get_res('SOLBUSD', sol_qty), x='time', y='res', color='red')
plt.xticks(rotation=45, size=5)
plt.show()

