# Using all the models and scalers in company-models, calls the correct model for every ticker 
# and uses that model to make a prediction off of current data
import pandas as pd
import numpy as np
from tensorflow import keras
import joblib
import os

def build_features(df):
    # exactlay matches the feature method used during training
    # load csv file into dataframe
    df = df.sort_values("date").reset_index(drop=True)

    # calculate returns
    df["return_1d"] = df["close"].pct_change()
    df["return_5d"] = df["close"].pct_change(5)
    df["return_10d"] = df["close"].pct_change(10)

    # moving averages
    df["ma_10"] = df["close"].rolling(window=10).mean()
    df["ma_50"] = df["close"].rolling(window=50).mean()
    df["price_vs_ma10"] = df["close"] / df["ma_10"] - 1
    df["price_vs_ma50"] = df["close"] / df["ma_50"] - 1

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

    return df

# model_path and scaler_path adjusted for calls from backend.py (python only considers files relative to the file that is running)
def predict_latest(ticker):
    # model_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "model", f"company_models.{ticker}_long_term_model.keras")
    # scaler_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "model", f"company_models.{ticker}_model.scaler.pk1")
    model_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "company_models",f"{ticker}_long_term_model.keras")
    scaler_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "company_models",f"{ticker}_model.scaler.pk1")
    feature_cols = [
        "return_1d", "return_5d", "return_10d",
        "price_vs_ma10", "price_vs_ma50",
        "rsi_14", "volatility_10d",
        "volume_change", "volume_vs_avg20",
    ]

    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "..", "stock_data", f"{ticker}_5yr_data.csv")

    # load price data current for this ticker - CHANGE IF CHANGE NAMES OF CSV FILES
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])

    # build same features using above data
    df = build_features(df)
    # drop any None rows
    df = df.dropna(subset=feature_cols).reset_index(drop=True)

    if df.empty:
        raise ValueError(f"Not enough data for {ticker}")
    
    # take most recent row 
    latest_row = df.iloc[[-1]][feature_cols].values
    latest_date = df.iloc[-1]["date"]

    # load trained model and scaler fit used during training

    model = keras.models.load_model(model_path)
    scaler = joblib.load(scaler_path)

    # scale using training stats - do NOT re-fit
    latest_scaled = scaler.transform(latest_row)

    # predit
    # can consider using model.predict but is storage/memory-heavy
    probability = float(model(latest_scaled, verbose=0)[0][0])
    prediction = "BUY" if probability > 0.5 else "SELL"

    return prediction, probability

if __name__ == "__main__":
    ticker = input("Enter a ticker symbol: ").strip().upper()
    predict_latest(ticker)
