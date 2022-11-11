import csv
import pandas as pd
from binance import Client
import time
from api_keys import api_key, secret
import pandas_ta as pta
from ta.trend import STCIndicator

client = Client(api_key=api_key, api_secret=secret)


def get_data(symbol, interval, back_to):
    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, back_to + 'min ago UTC'))
    frame = frame.iloc[:, :6]
    frame.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
    frame = frame.set_index('time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame


def trading_strategy_1(symbol, interval, back_to, qty, open_position=False, long_open_position=False, short_open_position=False):
    # print('Position is not open')
    # loading historical data from binance
    try:
        df = get_data(symbol, interval, back_to)
    except:
        print('ERROR! Restart after 30 seconds')
        time.sleep(30)
        df = get_data(symbol, interval, back_to)

    # calculating indicators
    ema200 = pta.ema(df.close, 200)
    adx = pta.adx(df.high, df.low, df.close, 12).iloc[:, 0]
    stc = STCIndicator(df.close, window_slow=50, window_fast=26, cycle=12, fillna=True).stc()
    stc_line = str(df[df.index == df.index[-1]].reset_index())
    print(stc_line)
    print(f'{symbol}   stc[-2] = {stc[-2]}    stc[-1] = {stc[-1]}    adx = {adx[-1]}\n')
    # condition for long open
    if (df.close[-1] > ema200[-1] or df.high[-1] > ema200[-1]) and \
            (stc[-2] < stc[-1] < 25) and \
            (adx[-1] >= 20):
        # print('Indicators gives a signal to BUY!')
        try:
            order = client.create_test_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty)
        except:
            print('ERROR! Retry to place an order in 30 seconds')
            time.sleep(30)
            order = client.create_test_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty)

        # order price, sl, tp
        long_open_price = df.close[-1]
        long_stop_loss = df.low[-2]
        long_take_profit = long_open_price + (long_open_price - long_stop_loss) * 2

        with open('trading_strategy_1.csv', 'a') as file:
            wr = csv.writer(file)
            wr.writerow([df.index[-1], -long_open_price, None, None, None, symbol])
        long_open_position = True
        open_position = True
        print(f'{df.index[-1]}: long open ordered for {symbol} at {long_open_price} with stoploss={long_stop_loss} and take profit={long_take_profit}\n')

    # condition for short open
    if (df.close[-1] < ema200[-1] or df.low[-1] < ema200[-1]) and \
            (stc[-2] > stc[-1] > 75) and \
            (adx[-1] >= 20):
        # print('Indicators gives a signal to SELL!')
        try:
            order = client.create_test_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty)
        except:
            print('ERROR! Retry to place an order in 30 seconds')
            time.sleep(30)
            order = client.create_test_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty)

        # order price, sl, tp
        short_open_price = df.close[-1]
        short_stop_loss = df.high[-2]
        short_take_profit = short_open_price - (short_stop_loss - short_open_price) * 2

        with open('trading_strategy_1.csv', 'a') as file:
            wr = csv.writer(file)
            wr.writerow([df.index[-1], None, None, short_open_price, None, symbol])
        short_open_position = True
        open_position = True
        print(
            f'{df.index[-1]}: short open ordered for {symbol} at {short_open_price} with stoploss={short_stop_loss} and take profit={short_take_profit}\n')

    while open_position:
        time.sleep(60)
        try:
            df = get_data(symbol, interval, back_to)
        except:
            print('ERROR! Restart after 30 seconds.......')
            time.sleep(30)
            df = get_data(symbol, interval, back_to)

        if long_open_position:
            # print("Keeping a LONG open position....\n")
            if df.close[-1] <= long_stop_loss or df.close[-1] >= long_take_profit:
                # print('Signal to close open position!!')
                #order = client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty)
                #long_close_price = float(order['fills'][0]['price'])
                try:
                    order = client.create_test_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty)
                except:
                    print('ERROR! Retry to place an order in 30 seconds')
                    time.sleep(30)
                    order = client.create_test_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty)
                long_close_price = df.close[-1]
                with open('trading_strategy_1.csv', 'a') as file:
                    wr = csv.writer(file)
                    wr.writerow([df.index[-1], None, long_close_price, None, None, symbol])
                print(f'{df.index[-1]}: long position closed at {long_close_price} for {symbol}\n')
                break

        if short_open_position:
            #print("Keeping a SHORT open position....\n")
            if df.close[-1] <= short_take_profit or df.close[-1] >= short_stop_loss:
                try:
                    order = client.create_test_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty)
                except:
                    print('ERROR! Retry to place an order in 30 seconds')
                    time.sleep(30)
                    order = client.create_test_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty)
                short_close_price = df.close[-1]
                with open('trading_strategy_1.csv', 'a') as file:
                    wr = csv.writer(file)
                    wr.writerow([df.index[-1], None, None, None, -short_close_price, symbol])
                print(f'{df.index[-1]}: short position closed at {short_close_price} for {symbol}\n')
                break


def run_trading_1(symbol, interval, back_to, qty):
    while True:
        trading_strategy_1(symbol, interval, back_to, qty)
        time.sleep(60)









