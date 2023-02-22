import asyncio
import pybotters
import pandas as pd
import numpy as np
import talib
import math
from datetime import datetime, timedelta
import time
from loguru import logger

test_net = 'https://api-testnet.bybit.com'
main_net = 'https://api.bybit.com'

# settings
symbol = 'BTCUSDT'
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
                client.get('/public/linear/kline', params={
                    'symbol': symbol, 'interval': 1, 'from': int(time.time()) - 3600
                }), 
                client.get('/private/linear/order/list',
                            params={'symbol': symbol, 'order_status': 'New'}),
                client.get('/private/linear/position/list', params={'symbol': symbol}),
            )
            kline, order, position = await asyncio.gather(*[r.json() for r in resps])

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

            # 約定していないオーダー（アクティブな注文）を確認
            buy_order, sell_order = get_active_order(order['result']['data'])

            # n秒以上経過したオーダーがあればキャンセル
            if buy_order is not None:
                if is_within_seconds(buy_order['created_time'] , 30) == False:
                    data = await cancel(client, buy_order['order_id'])

            if sell_order is not None:
                if is_within_seconds(sell_order['created_time'] , 30 )== False:
                    data = await cancel(client, sell_order['order_id'])


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

            # ポジションを確認（約定済みのオーダーをチェック、損切りの判断）
            buy_position, sell_position = get_position(position['result'])

            # ポジションがなければ指値を出す
            if buy_position is None:
                data = await market(client, 'Buy', qty)
                # data = await limit(client, 'Buy', qty, buy_price[atr_period])
                #　ログをとる関数
                # 通知する関数

            if sell_position is None:
                data = await market(client, 'Sell', qty)
                # data = await limit(client, 'Sell', qty, sell_price[atr_period])

            # 注文する関数
            # ポジションを管理する関数

            # 待機(60秒)
            await asyncio.sleep(60.0)

async def market(client, side, qty):
    res = await client.post('/private/linear/order/create', data={
        'symbol': symbol,
        'side': side,
        'order_type': 'Market',
        'qty': qty,
        'time_in_force': 'GoodTillCancel',
        'reduce_only': False,
        'close_on_trigger': False
    })
    data = await res.json()
    logger.info(data)
    return data

async def limit(client, side, qty, price):
    res = await client.post('/private/linear/order/create', data={
        'symbol': symbol,
        'side': side,
        'order_type': 'Limit',
        'qty': qty,
        'price': price,
        'time_in_force': 'GoodTillCancel',
        'reduce_only': False,
        'close_on_trigger': False
    })
    data = await res.json()
    logger.info(data)
    return data

# https://bybit-exchange.github.io/docs-legacy/futuresV2/linear/#t-getactive
# https://bybit-exchange.github.io/docs-legacy/futuresV2/linear/#order-status-order_status-stop_order_status
def get_active_order(order):
    buy_order = None
    sell_order = None

    for o in order:
        if o['side'] == 'Buy':
            buy_order = o
        else:
            sell_order = o

    return buy_order, sell_order

# https://bybit-exchange.github.io/docs-legacy/futuresV2/linear/#t-myposition
def get_position(position):
    buy_position = None
    sell_position = None

    for pos in position:
        if pos['size'] == 0:
            continue
        if pos['side'] == 'Buy':
            buy_position = pos
        else:
            sell_position = pos

    return buy_position, sell_position

async def cancel(client, order_id):
    res = await client.post('/private/linear/order/cancel', data={
        'symbol': symbol,
        'order_id': order_id,
        # 'order_link_id': ''
    })
    data = await res.json()
    logger.info(data)
    return data

# アクティブなオーダーの経過時間を判定
def is_within_seconds(date_str, seconds):
    now = datetime.utcnow()
    target_time = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
    # 現在時刻と指定した時刻の差分を計算
    elapsed_time = now - target_time
    # 経過時間が指定した秒数以内ならTrueを返す
    return elapsed_time <= timedelta(seconds=seconds)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass