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
            async with pybotters.Client(base_url=url, apis=apis) as client:
                    r = await client.post(
                        '/private/linear/order/create', # USDT Perpetual
                        data = {
                            'symbol': 'BTCUSDT', # BTCUSDT - Maximum quantity of 100 for opening; Maximum quantity of 100 for closing
                            'side': side, # Buy / Sell
                            'order_type': type, # Limit / Market
                            'qty': qty, # number
                            'price': price, # number
                            'time_in_force': 'PostOnly',
                            'reduce_only': False,
                            'close_on_trigger': False}
                    )
                    data = await r.json()
                    print(data)
                    break
        except asyncio.TimeoutError as e:
            print('Error: ', e)
            time.sleep(10)
        return data

# TEST
# async def main():
#     data = await order('Sell', 'Market', 0.001, 31330)
#     print(data)

# try:
#     asyncio.run(main())
# except KeyboardInterrupt:
#     pass
