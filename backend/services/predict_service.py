import pandas as pd
import yfinance as yf
from elastic import scroll_index
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np
from datetime import datetime, timedelta


from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler


def get_sentiment_df(ticker):
    query = {"match": {"metadata.ticker": ticker}}
    results = scroll_index("stock-sentiment", query)
    if not results:
        return pd.DataFrame()

    data = [doc["_source"] for doc in results]
    df = pd.json_normalize(data)
    
    # Convert and clean date column
    df["date"] = pd.to_datetime(df["created_at"]).dt.normalize()
    
    # Aggregate with enhanced null handling
    grouped = df.groupby("date", as_index=False).agg(
        avg_confidence=("confidence", lambda x: x.mean(skipna=True)),
        post_count=("confidence", "size"),
        mode_sentiment=("sentiment", lambda x: x.mode()[0] if not x.mode().empty else "neutral")
    )
    return grouped

def get_stock_data(ticker, start, end):
    # Ensure single ticker format
    if isinstance(ticker, list):
        ticker = ticker[0]
    
    # Download data with single ticker format
    stock = yf.download(ticker, start=start, end=end, auto_adjust=False)
    print(stock)
    # Flatten MultiIndex columns if they exist
    if isinstance(stock.columns, pd.MultiIndex):
        stock.columns = stock.columns.get_level_values(0)
    
    stock.reset_index(inplace=True)
    stock["date"] = pd.to_datetime(stock["Date"]).dt.date
    return stock[["date", "Open", "Close"]]

def create_lstm_model(input_shape):
    # Initialize a Sequential model (a linear stack of layers)
    model = Sequential()

    # Add the first LSTM layer
    # - 50 units (neurons) to learn temporal patterns
    # - return_sequences=True means this layer will output the full sequence to the next LSTM layer
    # - input_shape specifies the shape of each input sample (time steps, features)
    model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
    model.add(Dropout(0.2))
    model.add(LSTM(50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(1, activation='sigmoid'))
    
    # Define the optimizer
    # - Adam optimizer is an advanced gradient descent method that adapts the learning rate during training
    optimizer = Adam(learning_rate=0.001)

    # Compile the model
    # - optimizer: Adam optimizer for training
    # - loss: binary_crossentropy because this is a binary classification task
    # - metrics: track 'accuracy' during training and evaluation
    model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])

    # Return the fully constructed model
    return model

def predict_stock(ticker, start, end):
    # Data collection and preprocessing (same as before)
    sentiment_df = get_sentiment_df(ticker)
    stock_df = get_stock_data(ticker, start, end)
    
    if sentiment_df.empty or stock_df.empty:
        return {"error": "Missing data"}
    
    # Convert date columns in original DataFrames
    sentiment_df["date"] = pd.to_datetime(sentiment_df["date"])
    stock_df["date"] = pd.to_datetime(stock_df["date"])
    
    # Merge FULL DataFrames
    merged = pd.merge(
        sentiment_df,
        stock_df,
        on="date",
        how="inner"
    )
    
    # Verify merged columns
    required_cols = {'Open', 'Close'}
    if not required_cols.issubset(merged.columns):
        return {"error": f"Missing columns after merge: {required_cols - set(merged.columns)}"}
    
    # Feature engineering
    merged["direction"] = (merged["Close"] > merged["Open"]).astype(int)
    features = merged[["avg_confidence", "post_count"]]
    target = merged["direction"]
    
    # Time-series specific preprocessing
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_features = scaler.fit_transform(features)
    
    # Define time_steps explicitly
    time_steps = 10  # Define your preferred time window for sequences
    
    # Create sequences for LSTM
    def create_sequences(data, targets, indexes, time_steps=3):
        X, y, idxs = [], [], []
        for i in range(len(data)-time_steps):
            X.append(data[i:(i+time_steps)])
            y.append(targets[i+time_steps])
            idxs.append(indexes[i+time_steps])
        return np.array(X), np.array(y), np.array(idxs)

    # Prepare indexes
    merged = merged.reset_index(drop=True)  # Reset merged indexes to be safe
    indexes = merged.index.values

    X, y, idxs = create_sequences(scaled_features, target.values, indexes, time_steps)
    
    # Train-test split for time series
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    idxs_train, idxs_test = idxs[:split], idxs[split:]
    # Build and train LSTM model
    model = create_lstm_model((X_train.shape[1], X_train.shape[2]))
    history = model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=32,
        validation_split=0.1,
        verbose=0
    )
    
    train_loss = history.history['loss']
    val_loss = history.history['val_loss']
    print(train_loss)
    print(val_loss)

    # 1. Predict on the entire test set ONCE
    test_predictions = model.predict(X_test, verbose=0)
    test_predictions = (test_predictions > 0.5).astype(int).flatten()

    # 2. Predict the next day in one clean step
    last_sequence = scaled_features[-time_steps:]
    last_sequence = np.expand_dims(last_sequence, axis=0) 
    next_day_prediction = model.predict(last_sequence, verbose=0)
    next_day_direction = int((next_day_prediction > 0.5).astype(int).flatten()[0])

    # Historical price change (open to close percentage)
    merged["price_change_percent"] = (merged["Close"] - merged["Open"]) / merged["Open"] * 100
    avg_price_change_percent = merged["price_change_percent"].mean()

    # Calculate next day's predicted open/close prices based on historical average change
    last_close_price = merged["Close"].iloc[-1]
    predicted_close_price = last_close_price * (1 + avg_price_change_percent / 100)

    # Apply predicted direction to adjust the next day's prices
    if next_day_direction == 1:  # Predicted up
        predicted_open_price = last_close_price  # Open price will be today's close
        predicted_close_price = predicted_open_price * (1 + avg_price_change_percent / 100)
    else:  # Predicted down
        predicted_open_price = last_close_price  # Open price will be today's close
        predicted_close_price = predicted_open_price * (1 - avg_price_change_percent / 100)

    # Generate results (adapt your existing formatting)
    result = {
        "ticker": ticker,
        "accuracy": f"{accuracy_score(y_test, test_predictions)*100:.2f}%",
        "predictions": []
    }

    # Add prediction details (same as before)
    for i, pred in enumerate(test_predictions):
        idx = idxs_test[i]
        row = merged.loc[idx]

        actual_price_change = row["Close"] - row["Open"]
        if pred == 1:
            predicted_price = row["Open"] + abs(actual_price_change)
        else:
            predicted_price = row["Open"] - abs(actual_price_change)

        result["predictions"].append({
            "date": row["date"].strftime("%Y-%m-%d"),
            "actual_direction": int(row["direction"]),
            "predicted_direction": int(pred),
            "open_price": round(row["Open"], 2),
            "close_price": round(row["Close"], 2),
            "actual_price_change": round(actual_price_change, 2),
            "predicted_price": round(predicted_price, 2)
        })

    # Add the next day's prediction
    next_day_date = merged["date"].max() + timedelta(days=1)  # Predict for the next day
    result["next_day_prediction"] = {
        "date": next_day_date.strftime("%Y-%m-%d"),
        "predicted_open_price": round(predicted_open_price, 2),
        "predicted_close_price": round(predicted_close_price, 2),
        "predicted_direction": next_day_direction
    }

    # Wrap up the result
    data_to_return = {
        "data": analyze_sentiment_trend(result, ticker),
        "result": result
    }
    return data_to_return

# def predict_stock(ticker, start, end):
#     # Load data
#     sentiment_df = get_sentiment_df(ticker)
#     stock_df = get_stock_data(ticker, start, end)

#     if sentiment_df.empty or stock_df.empty:
#         return {"error": "Missing data"}

#     sentiment_df["date"] = pd.to_datetime(sentiment_df["date"])
#     stock_df["date"] = pd.to_datetime(stock_df["date"])

#     # Merge sentiment with stock data
#     merged = pd.merge(sentiment_df, stock_df, on="date", how="inner")

#     # Ensure required price columns exist
#     required_cols = {'Open', 'Close'}
#     if not required_cols.issubset(merged.columns):
#         return {"error": f"Missing columns after merge: {required_cols - set(merged.columns)}"}

#     # Feature: Direction (1 if price went up, 0 otherwise)
#     merged["direction"] = (merged["Close"] > merged["Open"]).astype(int)

#     # Fill missing sentiment features with 0
#     sentiment_features = [
#         "+avg_confidence", "-avg_confidence", "avg_neutral_confidence",
#         "+post_count", "-post_count", "neutral_count"
#     ]
#     for col in sentiment_features:
#         if col not in merged.columns:
#             merged[col] = 0
#         merged[col] = merged[col].fillna(0)

#     # Select features for model
#     features = merged[sentiment_features]
#     target = merged["direction"]

#     # Normalize
#     scaler = MinMaxScaler()
#     scaled_features = scaler.fit_transform(features)

#     time_steps = 3

#     def create_sequences(data, targets, indexes, time_steps=3):
#         X, y, idxs = [], [], []
#         for i in range(len(data)-time_steps):
#             X.append(data[i:(i+time_steps)])
#             y.append(targets[i+time_steps])
#             idxs.append(indexes[i+time_steps])
#         return np.array(X), np.array(y), np.array(idxs)

#     merged = merged.reset_index(drop=True)
#     indexes = merged.index.values
#     X, y, idxs = create_sequences(scaled_features, target.values, indexes, time_steps)

#     # Time series split
#     split = int(0.8 * len(X))
#     X_train, X_test = X[:split], X[split:]
#     y_train, y_test = y[:split], y[split:]
#     idxs_train, idxs_test = idxs[:split], idxs[split:]

#     # Train model
#     model = create_lstm_model((X_train.shape[1], X_train.shape[2]))
#     model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.1, verbose=0)

#     # Predict test set
#     test_predictions = model.predict(X_test, verbose=0)
#     test_predictions = (test_predictions > 0.5).astype(int).flatten()

#     # Predict next day
#     last_sequence = scaled_features[-time_steps:]
#     last_sequence = np.expand_dims(last_sequence, axis=0)
#     next_day_prediction = model.predict(last_sequence, verbose=0)
#     next_day_direction = int((next_day_prediction > 0.5).astype(int).flatten()[0])

#     # Price change % for estimating next close
#     merged["price_change_percent"] = (merged["Close"] - merged["Open"]) / merged["Open"] * 100
#     avg_price_change_percent = merged["price_change_percent"].mean()

#     last_close_price = merged["Close"].iloc[-1]
#     predicted_open_price = last_close_price
#     if next_day_direction == 1:
#         predicted_close_price = predicted_open_price * (1 + avg_price_change_percent / 100)
#     else:
#         predicted_close_price = predicted_open_price * (1 - avg_price_change_percent / 100)

#     # Format output
#     result = {
#         "ticker": ticker,
#         "accuracy": f"{accuracy_score(y_test, test_predictions) * 100:.2f}%",
#         "predictions": []
#     }

#     for i, pred in enumerate(test_predictions):
#         idx = idxs_test[i]
#         row = merged.loc[idx]
#         actual_price_change = row["Close"] - row["Open"]

#         if pred == 1:
#             predicted_price = row["Open"] + abs(actual_price_change)
#         else:
#             predicted_price = row["Open"] - abs(actual_price_change)

#         result["predictions"].append({
#             "date": row["date"].strftime("%Y-%m-%d"),
#             "actual_direction": int(row["direction"]),
#             "predicted_direction": int(pred),
#             "open_price": round(row["Open"], 2),
#             "close_price": round(row["Close"], 2),
#             "actual_price_change": round(actual_price_change, 2),
#             "predicted_price": round(predicted_price, 2)
#         })

#     result["next_day_prediction"] = {
#         "date": (merged["date"].max() + timedelta(days=1)).strftime("%Y-%m-%d"),
#         "predicted_open_price": round(predicted_open_price, 2),
#         "predicted_close_price": round(predicted_close_price, 2),
#         "predicted_direction": next_day_direction
#     }

#     return {
#         "data": analyze_sentiment_trend(result, ticker),
#         "result": result
#     }

# def predict_stock(ticker, start, end):
#     # Get data with validation
#     sentiment_df = get_sentiment_df(ticker)
#     stock_df = get_stock_data(ticker, start, end)
#     print(stock_df)
    
#     if sentiment_df.empty:
#         return {"error": "No sentiment data found"}
#     if stock_df.empty:
#         return {"error": "No stock data found"}
    
#     sentiment_df["date"] = pd.to_datetime(sentiment_df["date"])
#     stock_df["date"] = pd.to_datetime(stock_df["date"])
    
#     merged = pd.merge(sentiment_df, stock_df, on="date", how="inner")
#     if merged.empty:
#         return {"error": "No overlapping dates between sentiment and stock data"}
    
#     merged["direction"] = (merged["Close"] > merged["Open"]).astype(int)
    
#     X = merged[["avg_confidence", "post_count"]]
#     y = merged["direction"]
    
#     X_train, X_test, y_train, y_test = train_test_split(
#         X, y, test_size=0.2, random_state=42, shuffle=False
#     )
    
#     model = RandomForestClassifier()
#     model.fit(X_train, y_train)
    
#     predictions = model.predict(X_test)
#     accuracy = accuracy_score(y_test, predictions)
    
#     result = {
#         "ticker": ticker,
#         "accuracy": f"{round(accuracy * 100, 2)}%",
#         "predictions": []
#     }

#     for i, pred in enumerate(predictions):
#         idx = y_test.index[i]
#         row = merged.loc[idx]
        
#         actual_price_change = row["Close"] - row["Open"]
#         if pred == 1:
#             predicted_price = row["Open"] + abs(actual_price_change)
#         else:
#             predicted_price = row["Open"] - abs(actual_price_change)

#         result["predictions"].append({
#             "date": row["date"].strftime("%Y-%m-%d"),
#             "actual_direction": int(row["direction"]),
#             "predicted_direction": int(pred),
#             "open_price": round(row["Open"], 2),
#             "close_price": round(row["Close"], 2),
#             "actual_price_change": round(actual_price_change, 2),
#             "predicted_price": round(predicted_price, 2)
#         })

#     data_to_return = {
#         "data": analyze_sentiment_trend(result, ticker),
#         "result": result
#     }
#     return data_to_return
# def predict_stock(ticker, start, end):
#     # Get data with validation
#     sentiment_df = get_sentiment_df(ticker)
#     stock_df = get_stock_data(ticker, start, end)
    
#     # Handle empty cases
#     if sentiment_df.empty:
#         return {"error": "No sentiment data found"}
#     if stock_df.empty:
#         return {"error": "No stock data found"}
    
#     # Ensure consistent date types
#     sentiment_df["date"] = pd.to_datetime(sentiment_df["date"])
#     stock_df["date"] = pd.to_datetime(stock_df["date"])

#     # Merge with cleaned columns
#     merged = pd.merge(sentiment_df, stock_df, on="date", how="inner")
    
#     if merged.empty:
#         return {"error": "No overlapping dates between sentiment and stock data"}
    
#     # Create target variable
#     merged["direction"] = (merged["Close"] > merged["Open"]).astype(int)
    
#     # Model training and prediction
#     X = merged[["avg_confidence", "post_count"]]
#     y = merged["direction"]
    
#     X_train, X_test, y_train, y_test = train_test_split(
#         X, y, test_size=0.2, random_state=42, shuffle=False
#     )
    
#     model = RandomForestClassifier()
#     model.fit(X_train, y_train)
    
#     predictions = model.predict(X_test)
#     accuracy = accuracy_score(y_test, predictions)
    
#     # Prepare results with proper date formatting
#     result = {
#         "ticker": ticker,
#         "accuracy": round(accuracy, 2),
#         "predictions": [
#             {
#                 "date": merged.loc[y_test.index[i], "date"].strftime("%Y-%m-%d"),
#                 "actual": int(y_test.iloc[i]),
#                 "predicted": int(pred)
#             } for i, pred in enumerate(predictions)
#         ]
#     }
    
#     data_to_return = {"data": analyze_sentiment_trend(result, ticker), "result": result}
#     return data_to_return


def analyze_sentiment_trend(predictions, ticker):
    
    if not predictions or len(predictions) < 2:
        return {"error": "Not enough predictions to analyze sentiment trend."}
    
    # Ensure all entries have 'date' and 'predicted'
    cleaned = []
    for p in predictions["predictions"]:
        if "date" in p and "predicted_direction" in p:
            cleaned.append({
                "date": pd.to_datetime(p["date"]),
                "predicted": int(p["predicted_direction"])
            })

    if len(cleaned) < 2:
        return {"error": "Cleaned data is insufficient for analysis."}

    df = pd.DataFrame(cleaned).sort_values("date")

    mid = len(df) // 2
    prev_period = df.iloc[:mid]
    curr_period = df.iloc[mid:]

    prev_pos_ratio = prev_period["predicted"].mean() * 100
    curr_pos_ratio = curr_period["predicted"].mean() * 100

    if prev_pos_ratio == 0:
        change = "N/A"
    else:
        change = round((curr_pos_ratio - prev_pos_ratio) / prev_pos_ratio * 100, 2)

    overall_sentiment = "Positive" if curr_pos_ratio > 50 else "Negative"

    return {
        "ticker": ticker,
        "overall_sentiment": overall_sentiment,
        "current_positive_sentiment": f"{curr_pos_ratio:.2f}%",
        "previous_positive_sentiment": f"{prev_pos_ratio:.2f}%",
        "change_from_previous_period": f"{change}%" if change != "N/A" else "Insufficient data for change"
    }