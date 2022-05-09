#coding: utf-8
from rich import print
import pandas as pd
import datetime

# データフレームを取得
async def get_df(self):
    if self.backTest_flg:
        df = await self.get_df_from_csv()
    else:
        data = await self.get_market(60)
        df = await self.get_df_from_API(data)
    return df

# pandasのデータフレームに入れる
async def get_df_from_API(items):
    if items is None:
        return None

    date, open, high, low, close, volume = [],[],[],[],[],[]
    for item in items:
        date.append(datetime.datetime.fromtimestamp(item['open_time']))
        open.append(item['open'])
        high.append(item['high'])
        low.append(item['low'])
        close.append(item['close'])
        volume.append(item['volume'])

    df = pd.DataFrame({
        "date": date,
        "open": open,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume
    })

    # 時間をインデックスに設定して上書き
    df.set_index(["date"], inplace=True)
    return df

# pandasデータフレームに入れる(csv)
async def get_df_from_csv():
    df = pd.read_csv("./csv/14400_kline.csv", names=("date", "open", "high", "low", "close", "volume", "quoteVolume"))
    df.set_index(["date"], inplace=True)
    return df

# データフレームのリサンプル
async def reSample(rule, df):
    df_resampled = df.resample(rule)
    df_ohlc = df_resampled["close"].ohlc()
    return df_ohlc
