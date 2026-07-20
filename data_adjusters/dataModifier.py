import pandas as pd
import os
from pathlib import Path

# top 50 tech companies
tickers = [
    "NVDA",   # NVIDIA Corporation
    "AAPL",   # Apple Inc.
    "MSFT",   # Microsoft Corporation
    "GOOGL",  # Alphabet Inc. (Class A)
    "GOOG",   # Alphabet Inc. (Class C)
    "AMZN",   # Amazon.com Inc.
    "META",   # Meta Platforms Inc.
    "AVGO",   # Broadcom Inc.
    "TSLA",   # Tesla Inc.
    "ASML",   # ASML Holding N.V.
    "ADBE",   # Adobe Inc.
    "CSCO",   # Cisco Systems Inc.
    "INTC",   # Intel Corporation
    "AMD",    # Advanced Micro Devices Inc.
    "QCOM",   # Qualcomm Inc.
    "TXN",    # Texas Instruments Inc.
    "INTU",   # Intuit Inc.
    "AMAT",   # Applied Materials Inc.
    "MU",     # Micron Technology Inc.
    "ADI",    # Analog Devices Inc.
    "LRCX",   # Lam Research Corporation
    "KLAC",   # KLA Corporation
    "SNPS",   # Synopsys Inc.
    "CDNS",   # Cadence Design Systems Inc.
    "PANW",   # Palo Alto Networks Inc.
    "CRWD",   # CrowdStrike Holdings Inc.
    "FTNT",   # Fortinet Inc.
    "PYPL",   # PayPal Holdings Inc.
    "NFLX",   # Netflix Inc.
    "CMCSA",  # Comcast Corporation
    "PEP",    # PepsiCo Inc.
    "COST",   # Costco Wholesale Corporation
    "SBUX",   # Starbucks Corporation
    "MRVL",   # Marvell Technology Inc.
    "ADSK",   # Autodesk Inc.
    "WDAY",   # Workday Inc.
    "TEAM",   # Atlassian Corporation
    "ZS",     # Zscaler Inc.
    "DDOG",   # Datadog Inc.
    "MDB",    # MongoDB Inc.
    "SNOW",   # Snowflake Inc.
    "DOCU",   # DocuSign Inc.
    "OKTA",   # Okta Inc.
    "NXPI",   # NXP Semiconductors N.V.
    "MCHP",   # Microchip Technology Inc.
    "ON",     # ON Semiconductor Corporation
    "EA",     # Electronic Arts Inc.
    "ROKU",   # Roku Inc.
    "ZM",     # Zoom Communications Inc.
    "CTSH",   # Cognizant Technology Solutions Corp.
]

for ticker in tickers:
    # load csv file into dataframe
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "..", "stock_data", f"{ticker}_5yr_data.csv")

    # load price data current for this ticker - CHANGE IF CHANGE NAMES OF CSV FILES
    df = pd.read_csv(csv_path)

    # clean data of csv file
    prices = ["close","open", "high", "low"]
    for price in prices:
        df[price] = df[price].replace(r"[/$,]","",regex=True).astype(float)

    # convert volumes to int
    df["volume"] = df["volume"].replace(r"[/,]","",regex=True).astype(int)

    # sort dates from oldest -> newest
    # change based on display format of dates
    #df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    df["date"] = pd.to_datetime(df["date"], format="mixed")
    df = df.sort_values("date").reset_index(drop=True)

    # BEGIN EDITING CSV (DATAFRAME)
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

    # volatility
    df["volatility_10d"]= df["return_1d"].rolling(window=10).std()

    # volume
    df["volume_change"] = df["volume"].pct_change()
    df["volume_vs_avg20"] = df["volume"] / df["volume"].rolling(window=20).mean()

    # drop any rows that have na
    df = df.dropna().reset_index(drop=True)

    # compare each days close to next days close to predict the correct move to make
    df["next_close"] = df["close"].shift(-1)
    df["label"] = (df["next_close"] > df["close"]).map({True: "buy", False: "sell"})

    # drop last row since no "tomorrow"; label is unknown
    df = df.dropna(subset=["next_close"]).reset_index(drop=True)
    # drop "next_close" column
    df = df.drop(columns=["next_close"])
    #FINSH EDITING CSV(DATAFRAME)

    # convert back to csv and commit edits to file 
    df.to_csv(csv_path, index=False,date_format="%Y-%m-%d")
