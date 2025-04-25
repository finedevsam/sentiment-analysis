from elasticsearch import Elasticsearch
from config import ELASTIC_HOST

es = Elasticsearch(ELASTIC_HOST)

def search_index(index, query):
    return es.search(index=index, body={"query": query})

def count_index(index, query):
    return es.count(index=index, body={"query": query})

def scroll_index(index, query, scroll="2m", size=1000):
    page = es.search(index=index, body={"query": query}, scroll=scroll, size=size)
    sid = page["_scroll_id"]
    scroll_size = len(page["hits"]["hits"])
    results = page["hits"]["hits"]

    while scroll_size > 0:
        page = es.scroll(scroll_id=sid, scroll=scroll)
        sid = page["_scroll_id"]
        scroll_size = len(page["hits"]["hits"])
        results.extend(page["hits"]["hits"])

    return results