import traceback

from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

from finance.persistence.database import db
from finance.persistence.models import Dividend as div
from finance.persistence.models import MarketMovers as mm

from ai.sentiment_analyzer import SentimentAnalyzer
from finance.models.dividend_snapshot import DividendSnapshot
from finance.models.market_snapshot import MarketSnapshot
from finance.stock_quote import StockQuote
from news.news_fetcher import NewsFetcher

db.connect()
db.create_tables([div, mm])

app = Flask(__name__)
analyzer = SentimentAnalyzer()
dividend_snapshot = DividendSnapshot()
market_snapshot = MarketSnapshot()
stock_quote = StockQuote()
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
    dividends = div.select().order_by(div.ex_dividend_date.asc())
    
    data = [{
        "symbol": d.symbol,
        "name": d.name,
        "ex_dividend_date": str(d.ex_dividend_date),
        "dividend_per_share": d.dividend_per_share
    } for d in dividends]

    return jsonify({"upcoming_dividends": data})


# MARKET SNAPSHOT
@app.route("/market-movers", methods=["GET"])
def get_movers():
    gainers = mm.select().where(mm.snapshot_type == "gainer").order_by(mm.variation.desc())
    losers = mm.select().where(mm.snapshot_type == "loser").order_by(mm.variation.asc())

    return jsonify({
        "gainers": [{
            "symbol": g.symbol,
            "name": g.name,
            "price": g.price,
            "variation": g.variation,
            "volume_spike": g.volume_spike,
            "current_volume": g.current_volume,
            "avg_volume": g.avg_volume
        } for g in gainers],
        "losers": [{
            "symbol": l.symbol,
            "name": l.name,
            "price": l.price,
            "variation": l.variation,
            "volume_spike": l.volume_spike,
            "current_volume": l.current_volume,
            "avg_volume": l.avg_volume
        } for l in losers]
    })

@app.route("/market-trending", methods=["GET"])
def get_trending():
    trending = mm.select().where(mm.snapshot_type == "trending").order_by(mm.volume_spike.desc())
    
    return jsonify({
        "trending": [{
            "symbol": t.symbol,
            "name": t.name,
            "price": t.price,
            "variation": t.variation,
            "volume_spike": t.volume_spike,
            "current_volume": t.current_volume,
            "avg_volume": t.avg_volume
        } for t in trending]
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
    scheduler = BackgroundScheduler()
    scheduler.add_job(dividend_snapshot.update_upcoming_dividends, "interval", days=1)
    scheduler.add_job(market_snapshot.update_market_data, "interval", hours=1)
    scheduler.start()

    # dividend_snapshot.update_upcoming_dividends()
    market_snapshot.update_market_data()

    app.run(host="0.0.0.0", port=5001, debug=False)
