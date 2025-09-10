class Config:
    CSV_PATH = "/Users/silemobayo/Documents/MSC-PROJECT/stock-prediction/data.csv"
    TICKER_MAPPING = {
        "AMD": "AMD",
        "Google": "GOOGL",
        "Apple": "AAPL",
        "Tesla": "TSLA",
        "Netflix": "NFLX",
        "Nvidia": "NVDA",
        "Microsoft": "MSFT",
        "Youtube": "GOOGL",
        "Amazon": "AMZN",
        "Twitch": "AMZN",
    }
    
    # CSV Structure
    DATE_COL = "created_at"
    TEXT_COL = "text"
    GROUP_COL = "group_name"
    USER_COLS = ["screenname", "username", "followers", "friends"]
    METRIC_COLS = ["retweet_count", "polarity"]
    
    # Model Settings
    MODEL_NAME = "ProsusAI/finbert"
    BATCH_SIZE = 512
    CHUNK_SIZE = 10000
    
    # Elasticsearch
    ES_HOSTS = ["http://localhost:9200"]
    ES_USER = "elastic"
    ES_PASSWORD = "your_password"
    SENTIMENT_INDEX = "stock-sentiment"
    PREDICTION_INDEX = "market-predictions"
    
    # Time Settings
    LOOKBACK_DAYS = 30
    PREDICTION_HORIZON = 1