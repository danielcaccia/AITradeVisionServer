import traceback

from flask import Flask, request, jsonify

from ai.sentiment_analyzer import SentimentAnalyzer
from finance.stock_quote import StockQuote
from finance.market_snapshot import MarketSnapshot
from finance.dividend_snapshot import DividendSnapshot
from news.news_fetcher import NewsFetcher

app = Flask(__name__)
analyzer = SentimentAnalyzer()
stock_quote = StockQuote()
market_snapshot = MarketSnapshot()
dividend_snapshot = DividendSnapshot()
news_fetcher = NewsFetcher(analyzer)

# SENTIMENT ANALYZER
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
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


# YFINANCE
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
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route("/stock-history", methods=["GET"])
def stock_history():
    symbol = request.args.get("symbol")
    if not symbol:
        return jsonify({"error": "Stock symbol is required"}), 400

    result = stock_quote.get_history(symbol)
    return jsonify(result)

@app.route("/index-quote", methods=["GET"])
def get_index_quote():
    try:
        symbol = request.args.get("symbol", "")
        if not symbol:
            return jsonify({"error": "Stock symbol is required."}), 400

        result = stock_quote.get_index(symbol)
        if "error" in result:
            return jsonify(result), 404
        
        return jsonify(result)

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    
@app.route("/upcoming-dividends", methods=["GET"])
def upcoming_dividends():
    return jsonify({"upcoming_dividends": dividend_snapshot.upcoming_dividends})


# MARKET SNAPSHOT
@app.route("/market-movers", methods=["GET"])
def get_movers():
    return jsonify({
        "gainers": market_snapshot.market_cache["gainers"],
        "losers": market_snapshot.market_cache["losers"]
    })

@app.route("/market-trending", methods=["GET"])
def get_trending():
    return jsonify({
        "trending": market_snapshot.market_cache["trending"]
    })


# NEW API
@app.route("/latest-news", methods=["GET"])
def latest_news():
    try:
        query = request.args.get("q", "stock OR finance OR investing OR financial")
        news = news_fetcher.fetch_top_combined_news(query=query)

        return jsonify({"articles": news})
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@app.route("/stock-news", methods=["GET"])
def stock_news():
    try:
        symbol = request.args.get("symbol")

        if not symbol:
            return jsonify({"error": "Stock symbol is required."}), 400

        result = news_fetcher.fetch_news_for_symbol(symbol)

        return jsonify(result)
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    

if __name__ == "__main__":
    market_snapshot.start_market_snapshot_scheduler()
    dividend_snapshot.start_dividend_snapshot_scheduler()

    app.run(host="0.0.0.0", port=5001, debug=False)
