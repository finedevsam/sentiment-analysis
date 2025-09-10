import logging
import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from elasticsearch import Elasticsearch, helpers
from datasets import Dataset
from config import Config
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        self.device = 0 if torch.cuda.is_available() else -1
        self.tokenizer = AutoTokenizer.from_pretrained(Config.MODEL_NAME)
        self.model = AutoModelForSequenceClassification.from_pretrained(Config.MODEL_NAME)
        self.es = Elasticsearch(
            Config.ES_HOSTS,
            http_auth=(Config.ES_USER, Config.ES_PASSWORD),
            request_timeout=60
        )
    
    def process_data(self):
        """Process CSV with enhanced metadata handling"""
        dtype = {
            "followers": "Int64",
            "friends": "Int64",
            "retweet_count": "Int64"
        }
        
        for chunk in pd.read_csv(
            Config.CSV_PATH,
            chunksize=Config.CHUNK_SIZE,
            parse_dates=[Config.DATE_COL],
            dtype=dtype
        ):
            self._process_chunk(chunk)
    
    def _process_chunk(self, chunk):
        """Process chunk with metadata"""
        # Clean and filter data
        if 'group_name' in chunk.columns and hasattr(Config, 'TICKER_MAPPING'):
            chunk = chunk[chunk['group_name'].isin(Config.TICKER_MAPPING.keys())]
        
        # Ensure required columns exist
        required_cols = ['text']
        if Config.DATE_COL in chunk.columns:
            required_cols.append(Config.DATE_COL)
        
        chunk = chunk.dropna(subset=required_cols)
        
        if chunk.empty:
            logger.warning("No valid data to process after filtering")
            return
        
        # Clean the text column
        chunk['text'] = chunk['text'].apply(self._clean_text)
        
        # Explicitly get the column data we'll need later
        original_data = chunk.to_dict('records')
        
        # Prepare for sentiment analysis
        dataset = Dataset.from_pandas(chunk)
        dataset = dataset.map(self._tokenize, batched=True, batch_size=Config.BATCH_SIZE)
        
        # Set format only for columns that exist
        format_columns = ['input_ids', 'attention_mask']
        dataset.set_format('torch', columns=format_columns, 
                           device='cuda' if self.device == 0 else 'cpu')
        
        predictions = []
        idx = 0
        with torch.no_grad():
            for batch in dataset.iter(batch_size=Config.BATCH_SIZE):
                model_inputs = {k: v for k, v in batch.items() if k in ['input_ids', 'attention_mask']}
                outputs = self.model(**model_inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=1)
                confidence, labels = torch.max(probs, dim=1)
                
                # Use the batch size to determine how many records to process
                batch_size = len(labels)
                
                for i in range(batch_size):
                    if idx + i >= len(original_data):
                        break
                        
                    row_data = original_data[idx + i]
                    
                    # Create prediction dictionary with safe field access
                    prediction = {
                        "metadata": {
                            "ticker": Config.TICKER_MAPPING.get(row_data.get("group_name", ""), "UNKNOWN") 
                                     if hasattr(Config, 'TICKER_MAPPING') else "UNKNOWN",
                            "user": {}
                        },
                        "text": row_data.get("text", ""),
                        "sentiment": ["positive", "negative", "neutral"][labels[i].item()],
                        "confidence": confidence[i].item()
                    }
                    
                    # Add created_at if available
                    if "created_at" in row_data:
                        created_at = row_data["created_at"]
                        if hasattr(created_at, "tz_localize"):
                            created_at = created_at.tz_localize(None)  # Remove timezone info if already set
                        prediction["created_at"] = created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at)
                    
                    # Add user fields if available
                    user_fields = {
                        "screenname": row_data.get("screenname"),
                        "username": row_data.get("username")
                    }
                    
                    # Add numeric user fields with type checking
                    for field in ["followers", "friends"]:
                        if field in row_data and pd.notna(row_data[field]):
                            try:
                                user_fields[field] = int(row_data[field])
                            except (ValueError, TypeError):
                                user_fields[field] = None
                    
                    prediction["metadata"]["user"] = user_fields
                    
                    # Add other metadata if available
                    for field in ["location", "search_query"]:
                        if field in row_data:
                            prediction["metadata"][field] = row_data.get(field)
                    
                    # Add retweet_count if available
                    if "retweet_count" in row_data and pd.notna(row_data["retweet_count"]):
                        try:
                            prediction["metadata"]["retweet_count"] = int(row_data["retweet_count"])
                        except (ValueError, TypeError):
                            prediction["metadata"]["retweet_count"] = None
                    
                    # Add model metrics if available
                    model_metrics = {}
                    for metric in ["polarity", "partition_0", "partition_1"]:
                        if metric in row_data:
                            model_metrics[metric] = row_data[metric]
                    
                    if model_metrics:
                        prediction["model_metrics"] = model_metrics
                    
                    predictions.append(prediction)
                
                idx += batch_size
        
        if predictions:
            self._index_to_es(predictions)
        else:
            logger.warning("No predictions generated")
    
    def _clean_text(self, text):
        """
        Clean the text by removing URLs, hashtags, mentions, emojis, and other noise.
        """
        # Remove URLs
        text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
        
        # Remove hashtags
        text = re.sub(r"#\w+", "", text)
        
        # Remove mentions
        text = re.sub(r"@\w+", "", text)
        
        # Remove emojis
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F700-\U0001F77F"  # alchemical symbols
            u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            u"\U0001FA00-\U0001FA6F"  # Chess Symbols
            u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            u"\U00002702-\U000027B0"  # Dingbats
            u"\U000024C2-\U0001F251" 
            "]+", flags=re.UNICODE)
        text = emoji_pattern.sub(r"", text)
        
        # Remove extra spaces
        text = re.sub(r"\s+", " ", text).strip()
        
        return text
    
    def _tokenize(self, examples):
        return self.tokenizer(
            examples["text"],
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
    
    def _index_to_es(self, predictions):
        """Bulk index with enhanced error handling"""
        actions = ({
            '_op_type': 'index',
            '_index': Config.SENTIMENT_INDEX,
            '_source': pred
        } for pred in predictions)

        try:
            success, failed = helpers.bulk(
                self.es,
                actions,
                chunk_size=Config.BATCH_SIZE,
                request_timeout=60,
                raise_on_error=False
            )
            logger.info(f"Indexed {success} documents, {len(failed)} failed")
        except Exception as e:
            logger.error(f"Error indexing documents: {str(e)}")

if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    analyzer.process_data()