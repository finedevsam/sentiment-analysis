import pandas as pd
import re
from elasticsearch import Elasticsearch, helpers

# Initialize Elasticsearch client
es = Elasticsearch("http://localhost:9200")  # Replace with your Elasticsearch URL

# Load CSV file
csv_file_path = "/Users/silemobayo/Documents/PERSONAL-PROJECT/airflow/tech.csv"  # Path to the uploaded file
data = pd.read_csv(csv_file_path)

# Data Cleaning Function
def clean_text(text):
    """
    Cleans the tweet text by:
    - Removing hashtags (#)
    - Removing mentions (@)
    - Removing URLs
    - Removing special characters
    - Stripping extra whitespace
    """
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)  # Remove URLs
    text = re.sub(r"@\w+", "", text)  # Remove mentions
    text = re.sub(r"#\w+", "", text)  # Remove hashtags
    text = re.sub(r"[^A-Za-z0-9\s]", "", text)  # Remove special characters
    text = re.sub(r"\s+", " ", text).strip()  # Remove extra whitespace
    return text

# Data Cleaning
def clean_data(df):
    # Drop rows with null values in critical columns
    critical_columns = ["created_at", "text", "twitter_id", "polarity"]
    df = df.dropna(subset=critical_columns)

    # Convert numeric columns to proper types
    numeric_columns = ["followers", "friends", "retweet_count", "polarity"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")  # Convert and set invalid values as NaN
    df = df.dropna(subset=numeric_columns)  # Drop rows with invalid numeric data

    # Apply text cleaning to the 'text' column
    if "text" in df.columns:
        df["cleaned_text"] = df["text"].apply(clean_text)

    # Remove rows where 'cleaned_text' is empty or null after cleaning
    df = df[df["cleaned_text"].str.strip().astype(bool)]

    return df

# Clean the data
data = clean_data(data)

# Define Elasticsearch index
index_name = "twitter_tech_sentiment"  # Replace with your desired index name

# Check if the index exists, if not create it
if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name)

# Load data into Elasticsearch
def load_data_to_es(df, index_name):
    actions = []
    for record in df.to_dict(orient="records"):
        action = {
            "_index": index_name,
            "_source": {
                "created_at": record["created_at"],
                "file_name": record.get("file_name", None),
                "followers": record["followers"],
                "friends": record["friends"],
                "group_name": record.get("group_name", None),
                "location": record.get("location", None),
                "retweet_count": record["retweet_count"],
                "screenname": record.get("screenname", None),
                "search_query": record.get("search_query", None),
                "original_text": record["text"],
                "cleaned_text": record["cleaned_text"],
                "twitter_id": record["twitter_id"],
                "username": record.get("username", None),
                "polarity": record["polarity"],
                "partition_0": record.get("partition_0", None),
                "partition_1": record.get("partition_1", None),
            },
        }
        actions.append(action)

    # Bulk insert all documents
    if actions:
        helpers.bulk(es, actions)
        print(f"{len(actions)} records added to Elasticsearch.")
    else:
        print("No data to add.")

# Load cleaned data into Elasticsearch
if not data.empty:
    load_data_to_es(data, index_name)
else:
    print("No valid data to load into Elasticsearch.")
