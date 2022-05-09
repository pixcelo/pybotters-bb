import asyncio
from typing import Any, Dict

import motor.motor_asyncio
import pybotters

# BybitのWebSocketから約定履歴をデータベースに溜め込むスクリプト
class BybitMongoDB:
    def __init__(self):
        client = motor.motor_asyncio.AsyncIOMotorClient()
        db = client['bybit']
        self.collection = db['USDT']
        self.queue = asyncio.Queue()
        asyncio.create_task(self.consumer())

    def onmessage(self, msg: Dict[str, Any], ws):
        if 'topic' in msg:
            topic: str = msg['topic']
            if topic.startswith('trade'):
                self.queue.put_nowait(msg['data'])

    async def consumer(self):
        while True:
            data = await self.queue.get()
            await self.collection.insert_many(data)


async def main():
    async with pybotters.Client() as client:
        db = BybitMongoDB()
        wstask = await client.ws_connect(
            # 'wss://stream.bybit.com/realtime',
            'wss://stream.bybit.com/realtime_public', # USDT Perpetual
            # 'wss://stream.bytick.com/realtime_public', # USDT Perpetual
            send_json={'op': 'subscribe', 'args': ['trade.BTCUSDT']},
            hdlr_json=db.onmessage,
        )
        await wstask


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
