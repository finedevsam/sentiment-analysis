import os


ELASTIC_HOST = os.getenv("ELASTIC_HOST", "http://localhost:9200")
ELASTIC_USER = os.getenv("ELASTIC_USER", "")
ELASTIC_PASS = os.getenv("ELASTIC_PASS", "")
