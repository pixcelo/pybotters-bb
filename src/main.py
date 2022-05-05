#coding: utf-8
from csv import excel
from config import Config
from market import fetch_kline, fetch_market, fetch_ws
from rich import print
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import time
import datetime
import asyncio
from log import LogMan
import logging

# logger (※jupyterでは使用できない)
mg = LogMan(filename=F'./log/{datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")}.logs',
            level=logging.DEBUG)
# ====================================================================

class Trade:
    def __init__(self):
        self.symbol = "BTCJPY"
        self.backTest_flg = True

    # データフレームを取得
    async def get_df(self):
        if self.backTest_flg:
            df = await self.get_df_from_csv()
        else:
            data = await self.get_market(60)
            df = await self.get_df_from_API(data)
        return df

    # pandasのデータフレームに入れる
    async def get_df_from_API(seif, items):
        if items is None:
            return None

        date, open, high, low, close, volume = [],[],[],[],[],[]
        for item in items:
            date.append(datetime.datetime.fromtimestamp(item['open_time']))
            open.append(item['open'])
            high.append(item['high'])
            low.append(item['low'])
            close.append(item['close'])
            volume.append(item['volume'])

        df = pd.DataFrame({
            "date": date,
            "open": open,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume
        })

        # 時間をインデックスに設定して上書き
        df.set_index(["date"], inplace=True)
        return df

    # pandasデータフレームに入れる(csv)
    async def get_df_from_csv(self):
        df = pd.read_csv("./csv/14400_kline.csv", names=("date", "open", "high", "low", "close", "volume", "quoteVolume"))
        df.set_index(["date"], inplace=True)
        return df

    # pandasデータフレームの追加設定
    async def add_column(self, df):
        # windowはSMAの期間
        df["SMA25"] = df["close"].rolling(window=25).mean()
        df["SMA50"] = df["close"].rolling(window=50).mean()
        df["SMA100"] = df["close"].rolling(window=100).mean()
        df["SMA200"] = df["close"].rolling(window=200).mean()

        # diffは差分をとる df["close"].diff()
        df["change"] = df["close"].pct_change() # 1.0なら100%アップ、-0.5なら50%ダウン
        df["entry"] = df["change"] <= -0.01 # n%下落したらエントリー ex.-0.01 -> 1%の下落
        # print(df.dtypes)
        return df

    # データフレームのリサンプル
    async def reSample(self, rule, df):
        df_resampled = df.resample(rule)
        df_ohlc = df_resampled["close"].ohlc()
        return df_ohlc

    # グラフを表示する
    async def plot_graph(self, df):
        df.plot("date", ["close", "SMA"])
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.xticks(rotation=20) #横軸目盛の傾き
        yRange = [3000000, 3500000, 4000000, 4500000, 5000000, 5500000, 6000000, 6500000, 7000000, 7500000]
        plt.yticks(yRange)
        plt.show()

    # main logic
    async def main(self):
        #while True:
            # 長期足と中期足で環境確認、短期足でエントリーポイント確認
            data = await fetch_kline('D', '240', '60')
            df_day = await self.get_df_from_API(data[0]['result'])
            df_4h = await self.get_df_from_API(data[1]['result'])
            df_1h = await self.get_df_from_API(data[2]['result'])

            # インジケーターを追加
            df_day = await self.add_column(df_day)
            df_4h = await self.add_column(df_4h)
            df_1h = await self.add_column(df_1h)

            print(df_day)
            print(df_4h)
            print(df_1h)

            time.sleep(1)


# ====================================================================
trade = Trade()
# 非同期メイン関数を実行(Ctrl+Cで終了)
try:
    asyncio.run(trade.main())
except KeyboardInterrupt:
    pass
