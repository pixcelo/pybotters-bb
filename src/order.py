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
url_test = 'https://api-testnet.bybit.com'
wss_url = {
    'bybit'          :'wss://stream.bybit.com/realtime',
    'bybit_testnet'  :'wss://stream-testnet.bybit.com/realtime'
}

# 新規注文
async def order(side, type, qty, price=None):
    while True:
        try:
            async with pybotters.Client(base_url=url_test, apis=apis_test) as client:
                    r = await client.post(
                        '/private/linear/order/create', # USDT Perpetual
                        data = {
                            'symbol': 'BTCUSD', # BTCUSDT - Maximum quantity of 100 for opening; Maximum quantity of 100 for closing
                            'side': side, # Buy / Sell
                            'order_type': type, # Limit / Market
                            'qty': qty,
                            'price': price,
                            'time_in_force': 'PostOnly'}
                    )
                    data = await r.json()
                    print(data)
                    break
        except asyncio.TimeoutError as e:
            print('Error: ', e)
            time.sleep(10)
        return data
