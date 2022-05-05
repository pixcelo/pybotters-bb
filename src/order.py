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

# 新規注文
async def order(side, type, qty, price=None):
    while True:
        try:
            async with pybotters.Client(base_url='https://api.bybit.com', apis=apis) as client:
                    r = await client.post(
                        '/v2/private/order/create',
                        data = {
                            'symbol': 'BTCUSD',
                            'side': side,
                            'order_type': type, # Limit or Market
                            'qty': 1,
                            'price': price,
                            'time_in_force': 'PostOnly'}
                    )
                    data = await r.json()
                    # print(data)
                    break
        except asyncio.TimeoutError as e:
            print('Error: ', e)
            time.sleep(10)
        return data
