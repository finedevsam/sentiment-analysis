import pandas as pd
import yfinance as yf
from elastic import scroll_index
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


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
    
    # Flatten MultiIndex columns if they exist
    if isinstance(stock.columns, pd.MultiIndex):
        stock.columns = stock.columns.get_level_values(0)
    
    stock.reset_index(inplace=True)
    stock["date"] = pd.to_datetime(stock["Date"]).dt.date
    return stock[["date", "Open", "Close"]]

def predict_stock(ticker, start, end):
    # Get data with validation
    sentiment_df = get_sentiment_df(ticker)
    stock_df = get_stock_data(ticker, start, end)
    print(stock_df)
    
    if sentiment_df.empty:
        return {"error": "No sentiment data found"}
    if stock_df.empty:
        return {"error": "No stock data found"}
    
    sentiment_df["date"] = pd.to_datetime(sentiment_df["date"])
    stock_df["date"] = pd.to_datetime(stock_df["date"])
    
    merged = pd.merge(sentiment_df, stock_df, on="date", how="inner")
    if merged.empty:
        return {"error": "No overlapping dates between sentiment and stock data"}
    
    merged["direction"] = (merged["Close"] > merged["Open"]).astype(int)
    
    X = merged[["avg_confidence", "post_count"]]
    y = merged["direction"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=False
    )
    
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    
    result = {
        "ticker": ticker,
        "accuracy": f"{round(accuracy * 100, 2)}%",
        "predictions": []
    }

    for i, pred in enumerate(predictions):
        idx = y_test.index[i]
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

    data_to_return = {
        "data": analyze_sentiment_trend(result, ticker),
        "result": result
    }
    return data_to_return
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