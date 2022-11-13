import numpy as np
import pandas as pd
import pandas_ta as ta
from binance import Client
from api_keys import api_key, secret
import matplotlib.pyplot as plt
from ta.trend import STCIndicator
from plotly.subplots import make_subplots
import plotly.graph_objects as go



client = Client(api_key=api_key, api_secret=secret)

def get_hist_data(symbol, interval, back_to):
    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, back_to + 'min ago UTC'))
    frame = frame.iloc[:, :6]
    frame.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
    frame = frame.set_index('time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame

df = get_hist_data('BTCBUSD', '15m', '12000')
pd.set_option('display.max_columns', None)

# Indicators
stc = STCIndicator(df.close, window_slow=50, window_fast=26, cycle=12, fillna=True).stc()
stc_color = np.where(np.diff(np.array(stc), prepend=0) > 0, 'green', 'red')
stc_indicator = pd.DataFrame({'ind': stc, 'colors': stc_color})
df.ta.macd(close='close', fast=12, slow=26, signal=9, append=True)
ema5 = ta.ema(df['close'], 5)
ema20 = ta.ema(df['close'], 20)
ema200 = ta.ema(df['close'], 200)
volume_ma = ta.sma(df['volume'], 20)
adx = ta.adx(df.high, df.low, df.close, 12).iloc[:, 0]

# join all indicators into one dataframe
df_short = pd.concat([df, ema5, ema20, ema200, volume_ma, stc_indicator, adx], axis=1)
df_short.columns = [x.lower() for x in df_short.columns]
# take only last n candles
df_short = df_short.iloc[-200:, :]
#print(df_short.tail())

# 5 x 1 plotly figure
fig = make_subplots(rows=5, cols=1, shared_xaxes=True, vertical_spacing=.03, subplot_titles=['PRICE','MACD','VOLUME','ADX','STC'])

# ema5 line
fig.add_trace(
    go.Scatter(
        x=df_short.index,
        y=df_short.ema_5,
        line={'color': 'blue', 'width': 1},
        name='EMA 5',
        legendgroup='1'),
    row=1, col=1)

# ema20 line
fig.add_trace(
    go.Scatter(
        x=df_short.index,
        y=df_short.ema_20,
        line={'color': 'red', 'width': 1},
        name='EMA 20',
        legendgroup='1'),
    row=1, col=1)

# ema200 line
fig.add_trace(
    go.Scatter(
        x=df_short.index,
        y=df_short.ema_200,
        line={'color': 'purple', 'width': 2},
        name='EMA 200',
        legendgroup='1'),
    row=1, col=1)

# candlestick chart
fig.add_trace(
    go.Candlestick(
        x=df_short.index,
        open=df_short['open'],
        high=df_short['high'],
        low=df_short['low'],
        close=df_short['close'],
        increasing_line_color='green',
        decreasing_line_color='red',
        showlegend=False),
    row=1, col=1)

# fast macd signal
fig.add_trace(
    go.Scatter(
        x=df_short.index,
        y=df_short['macd_12_26_9'],
        line=dict(color='blue', width=1),
        name='MACD line',
        legendgroup='2'),
    row=2, col=1)

# slow macd signal
fig.add_trace(
    go.Scatter(
        x=df_short.index,
        y=df_short['macds_12_26_9'],
        line=dict(color='orange', width=1),
        name='MACD signal',
        legendgroup='2',
        legendgrouptitle_text='MACD'
    ),
    row=2, col=1)

# colorizing macd histogram
macd_colors = np.where(df_short['macdh_12_26_9'] < 0, 'red', 'green')

# macd histogram
fig.add_trace(
    go.Bar(
        x=df_short.index,
        y=df_short['macdh_12_26_9'],
        marker_color=macd_colors,
        showlegend=False),
    row=2, col=1)

# colorizing volume
volume_colors = np.where(np.diff(df_short['close'], prepend=0) > 0, 'green', 'red')

#add volume plot
fig.add_trace(
    go.Bar(
        x=df_short.index,
        y=df_short['volume'],
        marker_color=volume_colors,
        showlegend=False,
        legendgroup='3',
        legendgrouptitle_text='Volume'
    ),
    row=3, col=1)

# add the volume ma
fig.add_trace(
    go.Scatter(
        x=df_short.index,
        y=df_short.sma_20,
        name='volume MA',
        line=dict(color='blue', width=1),
        legendgroup='3',
        legendgrouptitle_text='Volume'
    ),
    row=3, col=1)

# add adx
fig.add_trace(go.Scatter(x=df_short.index,
                         y=df_short.adx_12,
                         mode='lines',
                         line_color='blue',
                         legendgroup='4',
                         name='ADX'), row=4, col=1)
# adx 20-level line
fig.add_hline(y=20, line_width=0.2, line_dash="dash", line_color="red", row=4, col=1)

# add stc
i = 1
while i < df_short.shape[0]-1:
    greens = pd.DataFrame()
    reds = pd.DataFrame()

    if df_short.iloc[i, 12] >= df_short.iloc[i-1, 12]:
        while i < df_short.shape[0]-1 and df_short.iloc[i, 12] >= df_short.iloc[i-1, 12]:
            greens = pd.concat([greens, df_short.iloc[[i-1]]], axis=0)
            greens = pd.concat([greens, df_short.iloc[[i]]], axis=0)
            i += 1
        fig.add_trace(go.Scatter(x=greens.index,
                                 y=greens.ind,
                                 mode='markers+lines',
                                 marker_color='green',
                                 line_color='green',
                                 showlegend=False,
                                 legendgroup='5',
                                 ), row=5, col=1)

    if df_short.iloc[i, 12] <= df_short.iloc[i-1, 12]:
        while i < df_short.shape[0]-1 and df_short.iloc[i, 12] <= df_short.iloc[i-1, 12]:
            reds = pd.concat([reds, df_short.iloc[[i - 1]]], axis=0)
            reds = pd.concat([reds, df_short.iloc[[i]]], axis=0)
            i += 1
        fig.add_trace(go.Scatter(x=reds.index,
                                 y=reds.ind,
                                 mode='markers+lines',
                                 marker_color='red',
                                 line_color='red',
                                 legendgroup='5',
                                 showlegend=False,
                                 ), row=5, col=1)

fig.add_hline(y=25, line_width=0.2, line_dash="dash", line_color="green", row=5, col=1)
fig.add_hline(y=75, line_width=0.2, line_dash="dash", line_color="red", row=5, col=1)


# prettifying
layout = go.Layout(
    plot_bgcolor='#efefef',
    font_family='Monospace',
    font_color='#000000',
    font_size=20,
    legend_tracegroupgap = 50,
    title_text='BTC/BUSD 15 min Timeframe Price Chart with Technical Indicators',
    xaxis=dict(rangeslider=dict(visible=False)))

# update options and show
fig.update_layout(layout)
fig.show()

