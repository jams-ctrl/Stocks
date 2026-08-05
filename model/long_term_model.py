# given various company csv's, makes a model and scaler for each company based on past features labeled in dataModifier.py
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report
import joblib
import os
import sys
# go up one parent folder
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from company_name_manager import get_top
# go down a parent folder
sys.path.remove(parent_dir)


# get top 50 companies
tickers = get_top()
# cycle through each company 
# no loop for now for debugging
for ticker in tickers:
    # load data
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "..", "stock_data", f"{ticker}_5yr_data.csv")

    df = pd.read_csv(csv_path)

    # define stock features - remove if want to limit features
    feature_cols = ["return_1d","return_5d","return_10d","price_vs_ma10","price_vs_ma50","rsi_14","volatility_10d","volume_change","volume_vs_avg20","macd_norm","macd_hist_norm","bb_position"]
    # extra cols: ,"macd_norm","macd_hist_norm","bb_position"
    # removed: ,"return_10d" ,"macd_norm","volatility_10d"

    X = df[feature_cols].values

    # map labels (strings) to integers
    label_map = {"sell": 0, "hold": 1, "buy":2}
    # define y as a list of these labels
    Y = df["label"].map(label_map).values

    # chronological train/test split (80%)
    split = int(len(df) * 0.8)
    X_train = X[:split]
    X_test = X[split:]
    Y_train = Y[:split]
    Y_test = Y[split:]

    # ensure features are in same range; scale them
    scaler = StandardScaler()
    # fits the data - calculates the mean and standard deviation of the data and uses that to rescale the data
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test) # do not fit; avoids leakage of data because 20% test data cannot be fitted on yet

    # class weights - hold is usually majority, so weight it down while weighing buy & sell up - or else model will only predict "hold"
    classes = np.array([0,1,2])
    weights = compute_class_weight("balanced", classes=classes, y=Y_train)
    class_weight_dict = {i: w for i, w, in zip(classes, weights)}



    # build neural network -> legacy model: 16, 8, 3
    model = keras.Sequential([
        # input layer
        keras.layers.Input(shape=(X_train_scaled.shape[1],)),
        keras.layers.Dense(16, activation="relu"),
        # any lower and model overfits immediately
        #keras.layers.Dropout(0.5),
        keras.layers.Dense(8, activation="relu"),
        keras.layers.Dense(4, activation="relu"),
        # output layer of 3
        keras.layers.Dense(3, activation="softmax"),
    ])

    model.compile(optimizer="adam",loss="sparse_categorical_crossentropy",metrics=["accuracy"])
    # make model stop once overfitting begins to occur
    early_stop = keras.callbacks.EarlyStopping(patience=5,restore_best_weights=True)
    # train model
    trained = model.fit(
        X_train_scaled, Y_train, 
        validation_split=0.2,
        # 10 times over, increase number for further training 
        epochs=50,
        batch_size=32,
        verbose=1,
        callbacks=[early_stop]
    )

    # evaluate on test set
    test_loss,test_acc = model.evaluate(X_test_scaled,Y_test)
    print(f"Loss: {test_loss:.4f} Accuracy: {test_acc:.4f}")

    # compare against baseline (always predicts majority)
    values, counts = np.unique(Y_test, return_counts=True)
    baseline_acc = counts.max()/counts.sum()
    print(f"Baseline(always predict majority class): {baseline_acc:.4f}")

    # ============DEBUG -> IMPROVE MODEL ACCURACY============

    # ============generate classification report on labels to see model accuracy
    #preds = np.argmax(model.predict(X_test_scaled), axis=1)
    #print(classification_report(Y_test, preds, target_names=["sell", "hold", "buy"]))

    # ============model check: correlation of new features with target -> should be 0.1 or higher to actually have correlation; anything under 0.02 is just noise
    # anticipate a more forward return - model can now look 5 days into the future
    df["target_return_10d"] = df["return_10d"].shift(-10)
    print(df[feature_cols].corrwith(pd.Series(Y)))
    # debug to show labels
    #print(df["label"].value_counts(normalize=True))
    # look at accuracy over ephochs & see if model is actually learning something
    # print(trained.history["accuracy"])
    # print(trained.history["val_accuracy"])
    # ============with all features 
    # Loss: 1.0758 Accuracy: 0.3952
    # Baseline(always predict majority class): 0.3901
    # return_1d         -0.005673
    # return_5d          0.006773
    # return_10d         0.002962
    # price_vs_ma10      0.005756
    # price_vs_ma50     -0.009695
    # rsi_14             0.011115
    # volatility_10d     0.010402
    # volume_change     -0.001589
    # volume_vs_avg20   -0.020897
    # macd_norm         -0.012288
    # macd_hist_norm     0.012356
    # bb_position        0.024191
    # dtype: float64
    # ============with less features
    # Loss: 1.0762 Accuracy: 0.3962
    # Baseline(always predict majority class): 0.3901
    # return_1d         -0.005673
    # return_5d          0.006773
    # price_vs_ma10      0.005756
    # price_vs_ma50     -0.009695
    # rsi_14             0.011115
    # volume_change     -0.001589
    # volume_vs_avg20   -0.020897
    # macd_hist_norm     0.012356
    # bb_position        0.024191
    # dtype: float64

    # ===========SAVE MODEL===========
    # save model to file located in company-models folder
    model.save(f"company_models/{ticker}_long_term_model.keras")

    # save scalar to preserve mean and stdev used during training
    joblib.dump(scaler, (f"company_models/{ticker}_model.scaler.pk1"))
