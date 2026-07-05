import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import StandardScaler

# load data
df = pd.read_csv("stock_data/AAPL_5yr_data_features.csv")

# define stock features 
feature_cols = ["return_1d","return_5d","return_10d","price_vs_ma10","price_vs_ma50","rsi_14","volatility_10d","volume_change","volume_vs_avg20"]

X = df[feature_cols].values
Y = (df["label"] == "buy").astype(int).values

# chronological train/test split (80%)
split = int(len(df) * 0.8)
X_train = X[:split]
X_test = x[split:]
Y_train = Y[:split]
Y_test = Y[split:]

# ensure features are in same range; scale them
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transfor(X_train) # do not fit; avoids leakage of data

# build neural network
model = keras.Sequential([
    # input layer
    keras.layers.Input(shape=(X_train_scaled.shape[1],)),
    keras.layers.Dense(16, activation="relu"),
    keras.layer.Dropout(0.5),
    keras.layers.Dense(8, activation="relu")
    # output layer
    keras.layers.Dense(1, activation="sigmoid")

])
