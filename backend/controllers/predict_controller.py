from flask import Blueprint, request, jsonify
from services.predict_service import predict_stock

predict_bp = Blueprint("predict", __name__)

@predict_bp.route("/predict", methods=["GET"])
def predict():
    ticker = request.args.get("ticker", "").upper()
    start = request.args.get("start")
    end = request.args.get("end")

    if not ticker or not start or not end:
        return jsonify({"error": "ticker, start, and end are required"}), 400

    try:
        result = predict_stock(ticker, start, end)
        return jsonify(result)
    except KeyError as e:
        return jsonify({"error": str(e)}), 500