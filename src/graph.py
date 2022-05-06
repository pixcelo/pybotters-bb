#coding: utf-8
import matplotlib.pyplot as plt

# データフレームのリサンプル
async def reSample(rule, df):
    df_resampled = df.resample(rule)
    df_ohlc = df_resampled["close"].ohlc()
    return df_ohlc

# グラフを表示する
async def plot_graph(df):
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.xticks(rotation=20) #横軸目盛の傾き
    df[['close', 'mean', 'upper', 'lower']].plot(
        grid=True,              # 罫線
        figsize=(20,5),         # 描画サイズ。インチ（横、縦）
        title="Close",          # グラフタイトル
        legend=True,            # 凡例
        rot=45,                 # xtick の ローテーション
        fontsize=15,            # 文字サイズ
        style={"close": "g--"}, # 色と線の種類,
    );
    plt.show()
