import yfinance as yf
import pandas as pd
import logging
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from elasticsearch import Elasticsearch
from config import Config

logger = logging.getLogger(__name__)

class MarketPredictor:
    def __init__(self):
        self.es = Elasticsearch(
            Config.ES_HOSTS,
            timeout=30
        )
        self.models = {}
    
    def run_pipeline(self):
        """Predict for all tickers"""
        for ticker in Config.TICKER_MAPPING.values():
            try:
                features, targets = self._prepare_data(ticker)
                if not features.empty:
                    model = self._train_model(features, targets)
                    prediction = self._predict(model, features)
                    self._index_prediction(ticker, prediction)
            except ValueError as ve:
                logger.info(str(ve))  # Log and skip the ticker if there's no social data
                continue
            except Exception as e:
                logger.error(f"Failed processing {ticker}: {str(e)}")

    def _prepare_data(self, ticker):
        """Prepare data with enhanced sentiment confidence handling"""
        query = {
            "size": 0,
            "query": {
                "term": {"metadata.ticker.keyword": ticker}
            },
            "aggs": {
                "hourly": {
                    "date_histogram": {
                        "field": "created_at",
                        "fixed_interval": "1h"
                    },
                    "aggs": {
                        "avg_sentiment": {"avg": {"field": "confidence"}},
                        "sum_retweets": {"sum": {"field": "metadata.retweet_count"}},
                        "avg_followers": {"avg": {"field": "metadata.user.followers"}}
                    }
                }
            }
        }

        try:
            result = self.es.search(index=Config.SENTIMENT_INDEX, body=query)
            print(f"Elasticsearch query result: {result}")
        except Exception as e:
            logger.error(f"Elasticsearch query failed: {str(e)}")
            return pd.DataFrame(), pd.Series()

        # Process results safely
        social_data = []
        if 'aggregations' in result and 'hourly' in result['aggregations'] and 'buckets' in result['aggregations']['hourly']:
            for bucket in result['aggregations']['hourly']['buckets']:
                social_impact = 0
                try:
                    sum_retweets = bucket.get('sum_retweets', {}).get('value', 0) or 0
                    avg_followers = bucket.get('avg_followers', {}).get('value', 0) or 0
                    avg_sentiment = bucket.get('avg_sentiment', {}).get('value', 0) or 0

                    # Calculate social impact based on retweets and followers
                    social_impact = (sum_retweets * (avg_followers / 1000)) if avg_followers else 0
                except (TypeError, KeyError):
                    pass

                social_data.append({
                    "datetime": pd.to_datetime(bucket['key_as_string']),
                    "sentiment_confidence": avg_sentiment,  # Use confidence as a feature
                    "social_impact": social_impact
                })

        if not social_data:
            logger.warning(f"No social data found for {ticker}, skipping.")
            return pd.DataFrame(), pd.Series()

        # Get market data with error handling
        try:
            logger.info(f"Downloading market data for {ticker}")
            stock_data = yf.download(ticker, period="60d", interval="60m")

            # Check if data was retrieved
            if stock_data.empty:
                logger.warning(f"No market data found for {ticker}")
                return pd.DataFrame(), pd.Series()

            # Handle multi-index if present
            if isinstance(stock_data.columns, pd.MultiIndex):
                stock_data.columns = stock_data.columns.droplevel(0)  # Drop the ticker level
            if isinstance(stock_data.index, pd.MultiIndex):
                stock_data = stock_data.droplevel(0, axis=0)  # Drop the first level (ticker symbol)
        except Exception as e:
            logger.error(f"Failed to download {ticker} data: {str(e)}")
            return pd.DataFrame(), pd.Series()

        # Create and prepare social data dataframe
        social_df = pd.DataFrame(social_data)
        social_df.set_index('datetime', inplace=True)

        logger.info(f"Social data shape: {social_df.shape}, Stock data shape: {stock_data.shape}")
        logger.info(f"Social data index type: {type(social_df.index)}")
        logger.info(f"Stock data index type: {type(stock_data.index)}")

        # Convert both indices to datetime with the same timezone (if needed)
        if social_df.index.tz is None:
            social_df.index = social_df.index.tz_localize('UTC')
        if stock_data.index.tz is not None:
            social_df.index = social_df.index.tz_convert(stock_data.index.tz)
        else:
            social_df.index = social_df.index.tz_localize(None)  # Remove timezone if stock data has none

        # Merge and process data
        try:
            merged = pd.merge(
                social_df,
                stock_data,
                left_index=True,
                right_index=True,
                how='inner'
            )

            logger.info(f"Merged data shape: {merged.shape}")

            if merged.empty:
                logger.warning(f"No overlapping data found for {ticker}")
                return pd.DataFrame(), pd.Series()
        except Exception as e:
            logger.error(f"Merge failed: {str(e)}")
            logger.info(f"Social df sample:\n{social_df.head()}")
            logger.info(f"Stock data sample:\n{stock_data.head()}")
            return pd.DataFrame(), pd.Series()

        # Feature engineering with sentiment confidence
        try:
            # Rolling statistics for sentiment confidence
            merged['sentiment_trend'] = merged['sentiment_confidence'].rolling('6h').mean().fillna(merged['sentiment_confidence'])
            merged['sentiment_volatility'] = merged['sentiment_confidence'].pct_change().fillna(0)

            # Social impact features
            merged['social_volatility'] = merged['social_impact'].pct_change().fillna(0)

            # Price momentum
            merged['price_momentum'] = merged['Close'].pct_change(4).fillna(0)

            # Final feature set
            features = merged[[
                'sentiment_confidence',
                'sentiment_trend',
                'sentiment_volatility',
                'social_impact',
                'social_volatility',
                'Volume',
                'price_momentum'
            ]].dropna()

            # Handle prediction horizon
            targets = merged['Close'].pct_change(
                Config.PREDICTION_HORIZON
            ).shift(-Config.PREDICTION_HORIZON)

            # Align features and targets
            common_index = features.index.intersection(targets.dropna().index)
            features = features.loc[common_index]
            targets = targets.loc[common_index]

            logger.info(f"Final features shape: {features.shape}, targets shape: {targets.shape}")
        except KeyError as e:
            logger.error(f"Missing required column: {str(e)}")
            return pd.DataFrame(), pd.Series()

        return features, targets

    def _train_model(self, features, targets):
        """Train a model with the features"""
        try:
            model = Pipeline([
                ('scaler', StandardScaler()),
                ('model', HistGradientBoostingRegressor(max_iter=100))
            ])
            
            model.fit(features, targets)
            logger.info(f"Model trained successfully")
            return model
        except Exception as e:
            logger.error(f"Model training failed: {str(e)}")
            return None

    def _predict(self, model, features):
        """Generate predictions"""
        if model is None:
            return None
            
        try:
            return model.predict(features.iloc[-1:])[-1]
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            return None

    def _index_prediction(self, ticker, prediction):
        """Store prediction in ES"""
        if prediction is None:
            return
            
        doc = {
            'ticker': ticker,
            'prediction': float(prediction),
            'timestamp': pd.Timestamp.now().isoformat(),
            'prediction_type': 'price_change_pct',
            'horizon': Config.PREDICTION_HORIZON
        }
        
        try:
            self.es.index(index=Config.PREDICTION_INDEX, document=doc)
            logger.info(f"Prediction indexed for {ticker}: {prediction:.4f}")
        except Exception as e:
            logger.error(f"Failed to index prediction: {str(e)}")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    predictor = MarketPredictor()
    predictor.run_pipeline()