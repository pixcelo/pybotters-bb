#coding: utf-8
from curses import window
from market import fetch_kline
from strategy import bollingerBand, sma, env
from graph import plot_graph
from rich import print
import pandas as pd
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
        self.symbol = 'BTCJPY'
        self.backTest_flg = True
        self.break_price = 0 # 高値(安値)ブレイクした時点の価格
        self.entry_price = 0 # エントリー価格

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

    # main logic
    async def main(self):
        #while True:
            # 現在のポジションを確認

            # 長期足と中期足で環境確認、短期足でエントリーポイント確認
            data = await fetch_kline('D', '240', '60')
            df_day = await self.get_df_from_API(data[0]['result'])
            df_4h = await self.get_df_from_API(data[1]['result'])
            df_1h = await self.get_df_from_API(data[2]['result'])

            # インジケーターを追加
            df_day = await sma(df_day)
            df_4h = await sma(df_4h)
            df_1h = await sma(df_1h)

            df_day = await bollingerBand(df_day)
            df_4h = await bollingerBand(df_4h)
            df_1h = await bollingerBand(df_1h)

            df_day = await env(df_day)
            df_4h = await env(df_4h)
            df_1h = await env(df_1h)

            print(df_day)
            print(df_4h)
            print(df_1h)

            # グラフを表示
            await plot_graph(df_1h)

            #　重要なニュースや指標、FOMCの時はbotを止める

            # 下降トレンド（長期足200SMAが100SMAよりも上にある）の時、短期足でボリンジャーバンドの高値にcloseがタッチしたら価格を変数に保持　
            # その価格を現在価格が下回ったらショートでエントリー、安値タッチで利確　エントリー中に高値タッチしたらナンピン買い増し


            # 上昇トレンド（長期足200SMAが100SMAよりも下にある）の時、短期足でボリンジャーバンドの安値にcloseがタッチしたら価格を変数に保持
            # その価格を現在価格が上回ったらロングでエントリー、高値タッチで利確　エントリー中に安値タッチしたらナンピン買い増し

            time.sleep(1)


# ====================================================================
trade = Trade()
# 非同期メイン関数を実行(Ctrl+Cで終了)
try:
    asyncio.run(trade.main())
except KeyboardInterrupt:
    pass
