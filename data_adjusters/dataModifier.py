# takes the data of the top 50 stock companies as downloaded by stockDownloader.py and computes various key features about the stock. 
# then, appends these features onto the csv file for the ai to be trained on 

import pandas as pd
import os
from pathlib import Path
import sys

def modify_data(df,path=None):
    df = df if path==None else pd.read_csv(path) 
    # clean data of csv file and set prices to floats
    prices = ["close","open", "high", "low"]
    for price in prices:
        try:
            df[price] = df[price].replace(r"[/$,]","",regex=True).astype(float)
        except ValueError:
            continue

    # convert volumes to int
    df["volume"] = df["volume"].replace(r"[/,]","",regex=True).astype(int)

    df["date"] = pd.to_datetime(df["date"], format="mixed")

    # commented out - doesnt work and I dont know how to fix it
    # drop any duplicate dates
    df = df.drop_duplicates(subset="date")
    # sort dates from oldest -> newest
    df = df.sort_values("date").reset_index(drop=True)

    # ----------BEGIN EDITING CSV (DATAFRAME)
    # calculate returns
    df["return_1d"] = df["close"].pct_change()
    df["return_5d"] = df["close"].pct_change(5)
    df["return_10d"] = df["close"].pct_change(10)

    # moving averages
    df["ma_10"] = df["close"].rolling(window=10).mean()
    df["ma_50"] = df["close"].rolling(window=50).mean()
    df["price_vs_ma10"] = df["close"] / df["ma_10"] - 1
    df["price_vs_ma50"] = df["close"] / df["ma_50"] - 1
    df = df.drop(columns=["ma_10","ma_50"])

    # relative strength index
    diff = df["close"].diff()
    # set range from 0-100
    gain = diff.clip(lower=0)
    loss = -diff.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain/avg_loss.replace(0, 1e-10)
    df["rsi_14"] = 100 - (100 / (1+rs))

    # volatility w/ standard deviation
    df["volatility_10d"]= df["return_1d"].rolling(window=10).std()

    # MACD - map trend momemtum and when it changes
    # ema is exponential moving average - weighted average more affected by present or near-present price changes then by past
    ema_12 = df["close"].ewm(span=12, adjust=False).mean()
    ema_26 = df["close"].ewm(span=26, adjust=False).mean()
    # draw a trendline of emas
    macd = ema_12 - ema_26
    # another trendline to compare macd against 
    macd_signal = macd.ewm(span=9, adjust=False).mean()
    df["macd_norm"] = macd/df["close"]
    # historic trendline of macd variations over long period of time -> captures momentum accel/deaccel.
    df["macd_hist_norm"] = (macd-macd_signal)/df["close"]

    # bollinger band 
    ma_20 = df["close"].rolling(window=20).mean()
    std_20 = df["close"].rolling(window=20).std()
    upper_band = ma_20 + 2 * std_20
    lower_band = ma_20 - 2 * std_20
    df["bb_position"] = (df["close"] - lower_band) / (upper_band - lower_band)
    # volume
    df["volume_change"] = df["volume"].pct_change()
    df["volume_vs_avg20"] = df["volume"] / df["volume"].rolling(window=20).mean()

    # tomorrow's return_1d, used as baseline to make "buy","hold", or "sell" label - used for ai to train
    df["target_return"] = df["return_1d"].shift(-1)

    # k = 0.3 is sweet spot for hold/buy/sell ratios
    k = 0.3
    min_floor = 0.0005
    vol_threshold = df["volatility_10d"] * k
    threshold = vol_threshold.clip(lower=min_floor)

    # assign label to said day's stock data based on the stock's returns exceeding a current threshold
    df["label"] = "hold"
    df.loc[df["target_return"] > threshold, "label"] = "buy"
    df.loc[df["target_return"] < -threshold, "label"] = "sell"

    # drop last row since no "tomorrow"; label is unknown
    df = df.dropna(subset=["target_return"]).reset_index(drop=True)
    # drop "target_return" column
    df = df.drop(columns=["target_return"])

    # drop any rows that have NA 
    df = df.dropna().reset_index(drop=True)

    #----------FINSHED EDITING CSV(DATAFRAME)
    # return dataframe
    return df
