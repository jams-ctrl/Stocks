import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import StandardScaler

# load data
df = pd.read_csv("stock_data/AAPL_5yr_data.csv")

# define stock features 
feature_cols = ["return_1d","return_5d","return_10d","price_vs_ma10","price_vs_ma50","rsi_14","volatility_10d","volume_change","volume_vs_avg20"]

X = df[feature_cols].values
Y = (df["label"] == "buy").astype(int).values

# chronological train/test split (80%)
split = int(len(df) * 0.8)
X_train = X[:split]
X_test = X[split:]
Y_train = Y[:split]
Y_test = Y[split:]

# ensure features are in same range; scale them
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test) # do not fit; avoids leakage of data

# build neural network
model = keras.Sequential([
    # input layer
    keras.layers.Input(shape=(X_train_scaled.shape[1],)),
    keras.layers.Dense(16, activation="relu"),
    keras.layers.Dropout(0.2),
    keras.layers.Dense(8, activation="relu"),
    # output layer
    keras.layers.Dense(1, activation="sigmoid"),
])

model.compile(optimizer="adam",loss="binary_crossentropy",metrics=["accuracy"])

# train model
trained = model.fit(
    X_train_scaled, Y_train, 
    validation_split=0.2,
    epochs=50,
    batch_size=32,
    verbose=1,
)

# evaluate on test set
test_loss,test_acc = model.evaluate(X_test_scaled,Y_test)
print(f"Loss: {test_loss:.4f} Accuracy: {test_acc:.4f}")

# compare against baseline
baseline_acc = max(Y_test.mean(), 1-Y_test.mean())
print(f"Baseline(always predict majority): {baseline_acc:.4f}")