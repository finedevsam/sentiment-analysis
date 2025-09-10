from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from sentiment_pipeline import SentimentAnalyzer
from market_predictor import MarketPredictor
from config import Config

default_args = {
    'owner': 'airflow',
    'retries': 3,
    'retry_delay': timedelta(minutes=15)
}

def run_sentiment():
    analyzer = SentimentAnalyzer()
    analyzer.process_data()

def run_prediction():
    predictor = MarketPredictor()
    predictor.run_pipeline()

with DAG(
    'market_sentiment_daily',
    default_args=default_args,
    schedule_interval='0 18 * * 1-5',  # 6PM UTC, Monday-Friday
    start_date=datetime(2023, 1, 1),
    catchup=False
) as dag:

    sentiment_task = PythonOperator(
        task_id='process_sentiment',
        python_callable=run_sentiment
    )

    prediction_task = PythonOperator(
        task_id='predict_market',
        python_callable=run_prediction
    )

    sentiment_task >> prediction_task