from flask import Blueprint, request, jsonify
from elastic import search_index, count_index

search_bp = Blueprint("search", __name__)

@search_bp.route("/search", methods=["GET"])
def search():
    ticker = request.args.get("ticker", "").upper()
    index = request.args.get("index", "stock-sentiment")

    if not ticker:
        return jsonify({"error": "Missing 'ticker' parameter"}), 400

    query = {
        "match": {
            "metadata.ticker": ticker
        }
    }

    try:
        print(count_index(index=index, query=query)["count"])
        res = search_index(index=index, query=query)
        hits = res["hits"]["hits"]
        return jsonify([hit["_source"] for hit in hits])
    except KeyError as e:
        return jsonify({"error": str(e)}), 500
    
    
# { id: 'AAPL', name: 'Apple Inc.' },
# { id: 'GOOGL', name: 'Alphabet Inc.' },
# { id: 'MSFT', name: 'Microsoft Corp.' },
# { id: 'AMZN', name: 'Amazon.com Inc.' },
# { id: 'META', name: 'Meta Platforms Inc.' },
# { id: 'TSLA', name: 'Tesla Inc.' },

# TICKER_MAPPING = {
#         "AMD": "AMD",
#         "Google": "GOOGL",
#         "Apple": "AAPL",
#         "Tesla": "TSLA",
#         "Netflix": "NFLX",
#         "Nvidia": "NVDA",
#         "Microsoft": "MSFT",
#         "Youtube": "GOOGL",
#         "Amazon": "AMZN",
#         "Twitch": "AMZN",
#     }