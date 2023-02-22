import asyncio
import pybotters
import pandas as pd
import numpy as np
import talib
import math
import datetime as dt
import time
from loguru import logger

test_net = 'https://api-testnet.bybit.com'
main_net = 'https://api.bybit.com'

# settings
qty = 0.001

# apis
apis = {
    "bybit_testnet": ["KAA3Gq8p8hqjFpROui", "FnZ8EdaOcSTsxtLtLLmgkB1EpRE43SouR3RS"],
}

async def main():
    async with pybotters.Client(
        apis=apis,
        base_url=test_net) as client:

        while True:
            # REST APIデータ並列リクエスト
            resps = await asyncio.gather(
                client.get('public/linear/kline', params={
                    'symbol': 'BTCUSD', 'interval': 1, 'from': int(time.time()) - 3600
                }),
                # https://bybit-exchange.github.io/docs-legacy/futuresV2/linear/#t-getactive
                client.get('private/linear/order/list', params={'symbol': 'BTCUSD'}),
                client.get('private/linear/position/list', params={'symbol': 'BTCUSD'}),
            )
            kline, order, position = await asyncio.gather(*[r.json() for r in resps])

            # シグナル計算
            # klineからdfを作る ATRを計算、シグなる判定、ロジック
            df = pd.DataFrame(kline['result'],
                    columns=[
                    'open_time',
                    # 'open',
                    'high',
                    'low',
                    'close',
                    # 'volume'
                    ])
            
            # データ型を変換
            df = df.astype({
                'high': 'float',
                'low': 'float',
                'close': 'float'
            })

            # オーダーを確認（指値を出したが、約定していないものをチェック）
            # 画面で言うとアクティブな注文、買いの注文、売りの注
            # アクティブな注文があれば、約定までN回待機する
            #　オーダーがなければ指値を出す


            # ポジションを確認（約定済みのオーダーをチェック、損切りの判断）
            # ポジションがなければ指値を出す

            cl = df['close'].values
            hi = df['high'].values
            lo = df['low'].values

            # ATR
            atr_period = 14
            atr = talib.ATR(hi, lo, cl, timeperiod=atr_period)

            # 閾値
            threshold = 0.5

            # 指値の価格
            buy_price = cl - (atr * threshold)
            sell_price = cl + (atr * threshold)

            
            if True:
                data = await market(client, 'Buy', qty)
                # data = await limit(client, 'Buy', qty, buy_price[atr_period])
                #     logger.info(data)
                #　ログをとる関数
                # 通知する関数

            # 注文する関数
            # ポジションを管理する関数

            # 待機(60秒)
            await asyncio.sleep(60.0)

async def market(client, side, qty):
    res = await client.post('/private/linear/order/create', data={
        'symbol': 'BTCUSDT',
        'side': side,
        'order_type': 'Market',
        'qty': qty,
        'time_in_force': 'GoodTillCancel',
        'reduce_only': False,
        'close_on_trigger': False
    })
    data = await res.json()
    return data

async def limit(client, side, qty, price):
    res = await client.post('/private/linear/order/create', data={
        'symbol': 'BTCUSDT',
        'side': side,
        'order_type': 'Limit',
        'qty': qty,
        'price': price,
        'time_in_force': 'GoodTillCancel',
        'reduce_only': False,
        'close_on_trigger': False
    })
    data = await res.json()
    return data

async def cancel(client):
    res = await client.post('/private/linear/order/cancel', data={
        'symbol': 'BTCUSDT',
        # 'order_id': '',
        # 'order_link_id': ''
    })
    data = await res.json()
    return data

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass