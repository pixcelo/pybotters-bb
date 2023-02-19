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
                client.get('/v2/public/kline/list', params={
                    'symbol': 'BTCUSD', 'interval': 1, 'from': int(time.time()) - 3600
                }),
                client.get('/v2/private/order', params={'symbol': 'BTCUSD'}),
                client.get('/v2/private/position/list', params={'symbol': 'BTCUSD'}),
            )
            kline, order, position = await asyncio.gather(*[r.json() for r in resps])

            # シグナル計算
            # klineからdfを作る ATRを計算、シグなる判定、ロジック

            # 注文する関数
            # ポジションを管理する関数
            # 通知する関数
            #　ログをとる関数
            cond = True #'Whether to execute...'
            side = 'Buy'
            qty = 0.001
            price = 22000

            # オーダー執行
            if cond:
                data = await limit(client, side, qty, price)
                logger.info(data)

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

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass