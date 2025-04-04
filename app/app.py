from flask import Flask, request, jsonify
from app.model.sentiment_analyzer import SentimentAnalyzer
from app.finance.stock_quote import StockQuote

app = Flask(__name__)
analyzer = SentimentAnalyzer()
stock_quote = StockQuote()

@app.route("/", methods=["GET"])
def home():
    return "FinBERT Sentiment Analysis API is running!"

@app.route("/analyze", methods=["POST"])
def analyze_sentiment():
    try:
        data = request.get_json()
        text = data.get("text", "")

        if not text:
            return jsonify({"error": "Text is required."}), 400

        sentiment = analyzer.analyze(text)
        return jsonify({"sentiment": sentiment})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/quote", methods=["GET"])
def get_stock_quote():
    try:
        symbol = request.args.get("symbol", "")
        if not symbol:
            return jsonify({"error": "Stock symbol is required."}), 400

        result = stock_quote.get_quote(symbol)
        if "error" in result:
            return jsonify(result), 404
        
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/stock-history", methods=["GET"])
def stock_history():
    symbol = request.args.get("symbol")
    if not symbol:
        return jsonify({"error": "Stock symbol is required"}), 400

    result = stock_quote.get_history(symbol)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
