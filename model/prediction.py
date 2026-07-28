# Using all the models and scalers in company-models, calls the correct model for every ticker 
# and uses that model to make a prediction off of current data
import pandas as pd
import numpy as np
from tensorflow import keras
import joblib
import os

def build_features(df):
    # exactly matches the feature method used during training
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
    # do not divide by 0
    rs = avg_gain/avg_loss.replace(0, 1e-10)
    df["rsi_14"] = 100 - (100 / (1+rs))

    # volatility
    df["volatility_10d"]= df["return_1d"].rolling(window=10).std()

    # volume
    df["volume_change"] = df["volume"].pct_change()
    df["volume_vs_avg20"] = df["volume"] / df["volume"].rolling(window=20).mean()

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
        "macd_norm", "macd_hist_norm", "bb_position",
    ]

    script_dir = os.path.dirname(os.path.abspath(__file__))
    # CHANGE path if desired path to csv files changes
    csv_path = os.path.join(script_dir, "..", "stock_data", f"{ticker}_5yr_data.csv")

    # load price data current for this ticker 
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

    # precdit
    # using model.predict but is storage/memory-heavy
    probabilities = model.predict(latest_scaled, verbose=0)[0]
    label_map={0: "SELL", 1: "HOLD", 2: "BUY"}
    # returns the class with the highest probability
    predicted_class = int(np.argmax(probabilities))
    prediction = label_map[predicted_class]
    confidence = float(probabilities[predicted_class])

    return prediction, confidence, {
        "sell": float(probabilities[0]),
        "hold": float(probabilities[1]),
        "buy": float(probabilities[2]),
    }

if __name__ == "__main__":
    ticker = input("Enter a ticker symbol: ").strip().upper()
    predict_latest(ticker)
