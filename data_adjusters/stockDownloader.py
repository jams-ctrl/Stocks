# Given the top 50 tech companies, scrapes yahoo finance for stock data and downloads it 
# in the form of .csv files
import requests
import pandas as pd
import os
import sys
from datetime import datetime, timezone
import yfinance as yf

def download_data(past, present, ticker):
    df = yf.download(ticker, start=past, end=present, progress=False)
 
    if df.empty:
        print(f"  no data returned for {ticker}")
        return None

    # flatten multiIndex columns (special aspect of yfinance)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    # lowercase all headers to match dataModifier.py
    df.columns = df.columns.str.lower()
    # bring out dates as seperate column instead of as an index
    df = df.reset_index().rename(columns={"Date": "date"})
    df = df[["date","close","volume","open","high","low"]]
    return df
