# takes the data of the top 50 stock companies as downloaded by stockDownloader.py and computes various key features about the stock. 
# then, appends these features onto the csv file for the ai to be trained on 

import pandas as pd
import os
from pathlib import Path
import sys
# go up one parent folder
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
# since went up one parent folder all function calls are made from the invisible "parent-folder" - must change in prediction.py to use the right filepath
from company_name_manager import get_top_50
# go down 1 parent folder
sys.path.remove(parent_dir)

# top 50 tech companies as seen in company_name_manager
tickers = get_top_50()

for ticker in tickers:
    # load csv file into dataframe
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # CHANGE csv path if path to csv files changes
    csv_path = os.path.join(script_dir, "..", "stock_data", f"{ticker}_5yr_data.csv")

    # load price data current for this ticker 
    df = pd.read_csv(csv_path)

    # clean data of csv file and set prices to floats
    prices = ["close","open", "high", "low"]
    for price in prices:
        df[price] = df[price].replace(r"[/$,]","",regex=True).astype(float)

    # convert volumes to int
    df["volume"] = df["volume"].replace(r"[/,]","",regex=True).astype(int)

    # handle both %Y-%m-%d and %m/%d/%Y - format is set at end
    df["date"] = pd.to_datetime(df["date"], format="mixed")
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
    rs = avg_gain/avg_loss
    df["rsi_14"] = 100 - (100 / (1+rs))

    # volatility w/ standard deviation
    df["volatility_10d"]= df["return_1d"].rolling(window=10).std()

    # volume
    df["volume_change"] = df["volume"].pct_change()
    df["volume_vs_avg20"] = df["volume"] / df["volume"].rolling(window=20).mean()

    # drop any rows that have NA 
    df = df.dropna().reset_index(drop=True)

    # compare each days close to next days close to label the correct move to make - used for AI to train
    df["next_close"] = df["close"].shift(-1)
    df["label"] = (df["next_close"] > df["close"]).map({True: "buy", False: "sell"})
    # drop last row since no "tomorrow"; label is unknown
    df = df.dropna(subset=["next_close"]).reset_index(drop=True)
    # drop "next_close" column
    df = df.drop(columns=["next_close"])

    #----------FINSHED EDITING CSV(DATAFRAME)

    # convert back to csv and commit edits to file - specify date format
    df.to_csv(csv_path, index=False,date_format="%Y-%m-%d")
