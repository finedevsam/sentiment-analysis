import pandas as pd
import yfinance as yf
from elastic import scroll_index
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
import numpy as np


def get_sentiment_df(ticker):
    query = {"match": {"metadata.ticker": ticker}}
    results = scroll_index("stock-sentiment", query)
    if not results:
        return pd.DataFrame()

    data = [doc["_source"] for doc in results]
    df = pd.json_normalize(data)
    df["date"] = pd.to_datetime(df["created_at"]).dt.normalize()
    
    grouped = df.groupby("date", as_index=False).agg(
        avg_confidence=("confidence", lambda x: x.mean(skipna=True)),
        post_count=("confidence", "size"),
        mode_sentiment=("sentiment", lambda x: x.mode()[0] if not x.mode().empty else "neutral")
    )
    return grouped


def get_stock_data(ticker, start, end):
    if isinstance(ticker, list):
        ticker = ticker[0]

    stock = yf.download(ticker, start=start, end=end, auto_adjust=False)

    # 🔧 Flatten MultiIndex columns if present
    if isinstance(stock.columns, pd.MultiIndex):
        stock.columns = ['_'.join([str(c) for c in col]).strip() for col in stock.columns.values]

    stock.reset_index(inplace=True)

    # 🔄 Rename variations of Open/Close if needed
    possible_open_cols = [col for col in stock.columns if "Open" in col]
    possible_close_cols = [col for col in stock.columns if "Close" in col and "Adj" not in col]

    if not possible_open_cols or not possible_close_cols:
        print("Columns available:", stock.columns.tolist())  # Debugging aid
        return pd.DataFrame()  # Trigger error fallback

    # Take first match for Open and Close
    open_col = possible_open_cols[0]
    close_col = possible_close_cols[0]

    stock["date"] = pd.to_datetime(stock["Date"]).dt.normalize()

    return stock[["date", open_col, close_col]].rename(
        columns={open_col: "Open", close_col: "Close"}
    )


def predict_stock(ticker, start, end):
    sentiment_df = get_sentiment_df(ticker)
    stock_df = get_stock_data(ticker, start, end)
    
    if sentiment_df.empty or stock_df.empty:
        return {"error": "Missing data"}
    
    sentiment_df["date"] = pd.to_datetime(sentiment_df["date"])
    stock_df["date"] = pd.to_datetime(stock_df["date"])

    merged = pd.merge(sentiment_df, stock_df, on="date", how="inner")
    
    required_cols = {'Open', 'Close'}
    if not required_cols.issubset(merged.columns):
        return {"error": f"Missing columns after merge: {required_cols - set(merged.columns)}"}

    # Create direction (label)
    merged["direction"] = (merged["Close"] > merged["Open"]).astype(int)

    # Features and target
    features = merged[["avg_confidence", "post_count"]]
    target = merged["direction"]

    # Scale features
    scaler = MinMaxScaler()
    scaled_features = scaler.fit_transform(features)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        scaled_features, target, test_size=0.2, shuffle=False
    )

    # Train Random Forest
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)

    # Predictions
    y_pred = rf_model.predict(X_test)

    # Accuracy
    accuracy = accuracy_score(y_test, y_pred)

    # Predict next day direction
    last_row = merged[["avg_confidence", "post_count"]].iloc[-1:]
    last_scaled = scaler.transform(last_row)
    next_day_direction = int(rf_model.predict(last_scaled)[0])

    # Estimate next day open/close prices
    merged["price_change_percent"] = (merged["Close"] - merged["Open"]) / merged["Open"] * 100
    avg_price_change_percent = merged["price_change_percent"].mean()

    last_close_price = merged["Close"].iloc[-1]
    predicted_open_price = last_close_price
    if next_day_direction == 1:
        predicted_close_price = predicted_open_price * (1 + avg_price_change_percent / 100)
    else:
        predicted_close_price = predicted_open_price * (1 - avg_price_change_percent / 100)

    result = {
        "ticker": ticker,
        "accuracy": f"{accuracy * 100:.2f}%",
        "predictions": []
    }

    test_indices = y_test.index
    for i, idx in enumerate(test_indices):
        row = merged.loc[idx]
        pred = y_pred[i]
        actual_price_change = row["Close"] - row["Open"]

        predicted_price = (
            row["Open"] + abs(actual_price_change)
            if pred == 1 else
            row["Open"] - abs(actual_price_change)
        )

        result["predictions"].append({
            "date": row["date"].strftime("%Y-%m-%d"),
            "actual_direction": int(row["direction"]),
            "predicted_direction": int(pred),
            "open_price": round(row["Open"], 2),
            "close_price": round(row["Close"], 2),
            "actual_price_change": round(actual_price_change, 2),
            "predicted_price": round(predicted_price, 2)
        })

    next_day_date = merged["date"].max() + timedelta(days=1)
    result["next_day_prediction"] = {
        "date": next_day_date.strftime("%Y-%m-%d"),
        "predicted_open_price": round(predicted_open_price, 2),
        "predicted_close_price": round(predicted_close_price, 2),
        "predicted_direction": next_day_direction
    }

    return {
        "data": analyze_sentiment_trend(result, ticker),
        "result": result
    }
    
    
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