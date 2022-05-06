#coding: utf-8
from rich import print

async def add_indicator(df):
    df = await sma(df)
    df = await bollingerBand(df)
    df = await trend(df)
    return df

# ボリンジャーバンド
async def bollingerBand(df):
    df['mean'] = df['close'].rolling(window=20).mean()  # 移動平均
    df['std'] = df['close'].rolling(window=20).std() # 標準偏差
    df['upper'] = df['mean'] + (df['std'] * 2) # 高値
    df['lower'] = df['mean'] - (df['std'] * 2) # 安値
    return df

# 移動平均線
async def sma(df):
    # windowはSMAの期間
    df['SMA25'] = df['close'].rolling(window=25).mean()
    df['SMA50'] = df['close'].rolling(window=50).mean()
    df['SMA100'] = df['close'].rolling(window=100).mean()
    df['SMA200'] = df['close'].rolling(window=200).mean()
    # df = df.fillna(0) # 欠損値をゼロ埋め
    return df

# 環境認識
async def trend(df):
    df['trend'] = df['SMA200'] < df['SMA100'] # True なら上昇トレンド
    df['break_up'] = df['close'] > df['upper'] # 高値をcolseが上抜け
    df['break_down']  = df['close'] < df['lower'] # 安値をcolseが下抜け
    return df

# ヒゲ取り
async def add_column(df):
    # diffは差分をとる df['close'].diff()
    df['change'] = df['close'].pct_change() # 1.0なら100%アップ、-0.5なら50%ダウン
    df['entry'] = df['change'] <= -0.01 # n%下落したらエントリー ex.-0.01 -> 1%の下落
    # print(df.dtypes)
    return df
