#coding: utf-8
from market import get_unixTimeStamp, fetch_latest_info
from strategy import add_indicator
from dfFactory import get_df_from_API, reSample
from dataBase import DataBase
from order import order
from graph import plot_graph
from rich import print
import pandas as pd
import pybotters
import json
import time
import datetime
import asyncio
from log import LogMan
import logging
from config import Config

# logger (※jupyterでは使用できない)
mg = LogMan(filename=F'./log/{datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")}.logs',
            level=logging.DEBUG)

cf = Config()
symbol = 'BTCUSDT'
apis = {'bybit': [cf.API_KEY, cf.API_SECRET]}
apis_test = {'bybit': [cf.TEST_KEY, cf.TEST_SECRET]}
url = 'https://api.bybit.com'
url_test = 'https://api-testnet.bybit.com'
wss_url = {
    'bybit'          :'wss://stream.bybit.com/realtime',
    'bybit_testnet'  :'wss://stream-testnet.bybit.com/realtime'
}

# ====================================================================

class Trade:
    def __init__(self):
        self.backTest_flg = True
        self.break_price = 0 # 高値(安値)ブレイクした時点の価格
        self.entry_price = 0 # エントリー価格
        self.trend = True # True:上昇トレンド False:下落トレンド

    # klineを取得
    async def fetch_kline(self, client, interval):
        while True:
            try:
                ut = get_unixTimeStamp(interval)
                r = await client.get('/public/linear/kline',
                                    params={'symbol': symbol,
                                            'interval': interval,
                                            'from': ut})
                data = await r.json()
                break
            except asyncio.TimeoutError as e:
                print('Error: ', e)
                time.sleep(10)
        return data

    # USDT Perpetual My position
    async def fetch_position(self, client):
        while True:
            try:
                r = await client.get('/private/linear/position/list', params={'symbol': 'BTCUSDT'})
                data = await r.json()
                break
            except asyncio.TimeoutError as e:
                print('Error: ', e)
                time.sleep(10)
        return data

    # TODO: resampleする
    # TODO: バックテストのdataframeに対して シグナルを出す
    # TODO: 損益を出す
    # TODO: グラフで視覚化する

    # main logic
    async def main(self):
        async with pybotters.Client(apis=apis_test, base_url=url_test) as client:
            while True:
                # 現在のポジションを確認
                d = await self.fetch_position(client)
                if d['result'] is not None:
                    print(d['result'])

                # mongDBからデータフレームを取得（バックテスト）
                # db = DataBase()
                # df_mongo = db.main()
                # print(df_mongo)
                # df_mongo_h = df_mongo.resample('H', label='right')
                # df_1h = df_mongo_h['close'].ohlc()
                # print(df_mongo_h)
                # break

                # APIからフェッチする場合
                # 長期足と中期足で環境確認、短期足でエントリーポイント確認
                data_day = await self.fetch_kline(client, 'D')
                data_4h = await self.fetch_kline(client, '240')
                data_1h = await self.fetch_kline(client, '60')
                # データフレームを取得
                df_day = await get_df_from_API(data_day['result'])
                df_4h = await get_df_from_API(data_4h['result'])
                df_1h = await get_df_from_API(data_1h['result'])
                # インジケーターを追加
                df_day = await add_indicator(df_day)
                df_4h = await add_indicator(df_4h)
                df_1h = await add_indicator(df_1h)
                print(df_day.tail(), df_4h.tail(), df_1h.tail(), sep="\n")

                # グラフを表示
                # await plot_graph(df_1h)

                # 長期足をみて環境認識をする（トレンドの把握と更新）
                print('上昇トレンド') if df_day.iloc[-1]['trend'] else print('下降トレンド')
                self.trend = df_day.iloc[-1]['trend']

                # 価格を更新
                last_data = await fetch_latest_info()
                last_price = last_data['result'][0]['price']
                print(f'現在の価格: {last_price}')

                #　重要なニュースや指標（雇用統計、CPI）、FOMCの時はbotを止める

                # 下降トレンド（長期足200SMAが100SMAより上にある）の時、短期足でボリンジャーバンドの高値にcloseがタッチしたら価格を変数に保持　
                # その価格を現在価格が下回ったらショートでエントリー、安値タッチで利確　エントリー中に高値タッチしたらナンピン買い増し
                # -> break_upが短期足でtrueかどうかを調べる
                break_point_list = df_1h.index[df_1h['break_up'] == True].tolist()
                if len(break_point_list) > 0:
                    # print(break_up_list[-1]) # 最新
                    self.break_price = df_1h.at[break_point_list[-1], 'close']
                    print(f'ブレイク価格: {self.break_price}')
                    # ブレイクした価格よりも現在の価格が、再度下落に転じたタイミングでエントリーする
                    # ここでエントリー待ちのループに入る
                    while True:
                        if last_price <= self.break_price:
                            # 注文を入れる
                            print("SELL")
                            sell = await order('Sell', 'Limit', 0.001, last_price)
                            break
                        else:
                            print('No order')
                    # time.sleep(1)
                    # continue
                # else:
                    # continue

                # 上昇トレンド（長期足200SMAが100SMAよりも下にある）の時、短期足でボリンジャーバンドの安値にcloseがタッチしたら価格を変数に保持
                # その価格を現在価格が上回ったらロングでエントリー、高値タッチで利確　エントリー中に安値タッチしたらナンピン買い増し
                # -> break_downが短期足でtrueかどうかを調べる
                # print(df_1h.loc[df_1h['break_down'] == True])

                time.sleep(1)
                break


# ====================================================================
trade = Trade()
# 非同期メイン関数を実行(Ctrl+Cで終了)
try:
    asyncio.run(trade.main())
except KeyboardInterrupt:
    pass
