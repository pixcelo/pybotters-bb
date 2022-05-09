#coding: utf-8
from config import Config
from rich import print
import pybotters
import asyncio
import time

symbol = 'BTCUSDT'
cf = Config()
apis = {'bybit': [cf.API_KEY, cf.API_SECRET]}
apis_test = {'bybit': [cf.TEST_KEY, cf.TEST_SECRET]}
url = 'https://api.bybit.com'
wss_url = {
    'bybit'          :'wss://stream.bybit.com/realtime',
    'bybit_testnet'  :'wss://stream-testnet.bybit.com/realtime'
}

# WebSocket
async def fetch_ws():
    async with pybotters.Client(apis=apis_test) as client:
        store = pybotters.BybitDataStore()
        wstask = await client.ws_connect(
            wss_url['bybit_testnet'],
            send_json = {'op': 'subscribe',
                        'args': [
                            "orderBook_200.100ms.BTCUSD",
                            'trade.BTCUSD',
                            'instrument_info.100ms.BTCUSD',
                            ]
                        },
            hdlr_json=store.onmessage,
        )

        # WebSocketでデータを受信するまで待機
        while not all([
            len(store.orderbook),
            len(store.instrument)
        ]):
            await store.wait()

        # メインループ
        while True:
            # データ参照
            data = dict(
                orderbook = store.orderbook.sorted(),
                instrument= store.instrument.get({'symbol':'BTCUSD'}),
                position  = store.position_inverse.find(),
                trade     = store.trade.find(),
                execution = store.execution.find(),
                order     = store.order.find()
            )

            print(data['instrument'])
            await asyncio.sleep(1)

# REST API
async def fetch_market():
    while True:
        try:
            async with pybotters.Client(apis=apis, base_url=url) as client:
                r = await client.get('/v2/public/tickers', params={'symbol': symbol})
                data = await r.json()
                break
        except asyncio.TimeoutError as e:
            print('Error: ', e)
            time.sleep(10)

    return data

# USDT Perpetual Latest Information for Symbol
# {'id': '112607529582', 'symbol': 'BTCUSDT', 'price': 36460, 'qty': 0.134, 'side': 'Sell', 'time': '2022-05-06T06:13:44.000Z', 'trade_time_ms': 1651817624868}
async def fetch_latest_info():
    while True:
        try:
            async with pybotters.Client(apis=apis, base_url=url) as client:
                r = await client.get('/public/linear/recent-trading-records', params={'symbol': symbol, 'limit': 5})
                data = await r.json()
                break
        except asyncio.TimeoutError as e:
            print('Error: ', e)
            time.sleep(10)

    return data


# kline
# async def fetch_kline(interval_1, interval_2, interval_3):
#     '''
#     1 - 1 minute
#     3 - 3 minutes
#     5 - 5 minutes
#     15 - 15 minutes
#     30 - 30 minutes
#     60 - 1 hour
#     120 - 2 hours
#     240 - 4 hours
#     360 - 6 hours
#     720 - 12 hours
#     D - 1 day
#     W - 1 week
#     M - 1 month
#     '''
#     while True:
#         try:
#             async with pybotters.Client(apis=apis, base_url=url) as client:
#                 # 長期足
#                 ut = get_unixTimeStamp(interval_1)
#                 r = await client.get('/public/linear/kline',
#                                     params={'symbol': symbol,
#                                             'interval': interval_1,
#                                             'from': ut
#                                     })
#                 data_long = await r.json()

#                 # 中期足
#                 ut = get_unixTimeStamp(interval_2)
#                 r = await client.get('/public/linear/kline',
#                                     params={'symbol': symbol,
#                                             'interval': interval_2,
#                                             'from': ut
#                     })
#                 data_middle = await r.json()

#                 # 短期足
#                 ut = get_unixTimeStamp(interval_3)
#                 r = await client.get('/public/linear/kline',
#                                     params={'symbol': symbol,
#                                             'interval': interval_3,
#                                             'from': ut
#                     })
#                 data_short = await r.json()

#                 break
#         except asyncio.TimeoutError as e:
#             print('Error: ', e)
#             time.sleep(10)
#     data = data_long, data_middle, data_short
#     return data

def get_unixTimeStamp(interval):
    ut = 0
    # case Day
    if interval == 'D':
        ut = int(time.time()) - 24 * 60 * 60 * 200
    # case minute
    else :
        # intertval(30min) * 60秒 * 200個
        ut = int(time.time()) - int(interval) * 60 * 200
    return ut
