from motor.motor_asyncio import AsyncIOMotorClient
from rich import print
import pandas as pd
import asyncio
import nest_asyncio
nest_asyncio.apply()

# https://www.codetd.com/ja/article/12850605
# mongoDbからデータフレームを取得
class DataBase:
    def __init__(self):
        self.address = '127.0.0.1'
        self.port = 27017
        self.database = 'bybit'
        self.collection = 'USDT'

    def main(self):
        db = self.client_database()
        loop = asyncio.get_event_loop()
        df = loop.run_until_complete(self.do_find(db))
        return df

    def client_database(self):
        client = AsyncIOMotorClient(self.address, self.port)
        db = client[self.database]
        return db

    async def do_find(self, db):
        cursor = db[self.collection].find()
        count = []
        async for document in cursor:
            count.append(document)
        df = pd.DataFrame(count)
        df.set_index('_id',inplace=True)
        return df

    print('-' * 80)
