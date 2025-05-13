import os
import traceback

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

# Import Services
from app.ai.nlp.sentiment_analyzer import SentimentAnalyzer
from app.news.news_fetcher import NewsFetcher
from app.finance.services.stock_quote import StockQuote

# Import DB
from app.persistence.database import db
from app.persistence.models import Dividend, Ipo, TechnicalSignal, MarketMovers, AiInsight

# Import Snapshots
from app.ai.llm.ai_insights_snapshot import AiInsightsSnapshot
from app.finance.snapshots.dividend_snapshot import DividendSnapshot
from app.finance.snapshots.ipo_snapshot import IPOSnapshot
from app.finance.snapshots.signals_snapshot import SignalSnapshot
from app.finance.snapshots.market_snapshot import MarketSnapshot

load_dotenv()

USE_DEV_ENDPOINT = os.getenv("USE_DEV_ENDPOINT")

db.connect()
db.create_tables([Dividend, Ipo, TechnicalSignal, MarketMovers, AiInsight])

app = Flask(__name__)
analyzer = SentimentAnalyzer()
news_fetcher = NewsFetcher(analyzer)
stock_quote = StockQuote()

dividend_snapshot = DividendSnapshot()
ipo_snapshot = IPOSnapshot()
signals_snapshot = SignalSnapshot()
market_snapshot = MarketSnapshot()
ai_insights_snapshot = AiInsightsSnapshot()

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


# AI PICKS
@app.route("/api/ai-picks", methods=["GET"])
def get_ai_picks():
    symbol = request.args.get("symbol")

    query = AiInsight.select().order_by(AiInsight.created_at.desc())

    if symbol:
        query = query.where(AiInsight.symbol == symbol)

    insights = query.limit(10)

    data = [{
        "symbol": i.symbol,
        "title": i.title,
        "summary": i.summary,
        "sentiment_score": i.sentiment_score,
        "volume_ratio": i.volume_ratio,
        "relevance_score": i.relevance_score,
        "published_at": str(i.published_at),
        "url": i.url,
        "source": i.source
    } for i in insights]

    return jsonify({"insights": data})


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
    dividends = Dividend.select().order_by(Dividend.ex_dividend_date.asc())
    
    data = [{
        "symbol": d.symbol,
        "name": d.name,
        "ex_dividend_date": str(d.ex_dividend_date),
        "dividend_per_share": d.dividend_per_share
    } for d in dividends]

    return jsonify({"upcoming_dividends": data})

@app.route("/upcoming-ipos", methods=["GET"])
def upcoming_ipos():
    ipos = Ipo.select().order_by(Ipo.ipo_date.asc())
    
    data = [{
        "symbol": i.symbol,
        "name": i.name,
        "exchange": i.exchange,
        "ipo_date": str(i.ipo_date),
        "price_range": i.price_range
    } for i in ipos]

    return jsonify({"upcoming_ipos": data})

@app.route("/technical-signals", methods=["GET"])
def get_signals():
    signals = TechnicalSignal.select().order_by(TechnicalSignal.created_at.desc())
    
    data = [{
        "symbol": s.symbol,
        "name": s.name,
        "last_price": s.last_price,
        "rsi": s.rsi,
        "macd_cross": s.macd_cross,
        "signal_summary": s.signal_summary,
        "created_at": s.created_at
    } for s in signals]

    return jsonify({"technical_signals": data})


# MARKET SNAPSHOT
@app.route("/market-movers", methods=["GET"])
def get_movers():
    gainers = MarketMovers.select().where(MarketMovers.snapshot_type == "gainer").order_by(MarketMovers.variation.desc())
    losers = MarketMovers.select().where(MarketMovers.snapshot_type == "loser").order_by(MarketMovers.variation.asc())

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
    trending = MarketMovers.select().where(MarketMovers.snapshot_type == "trending").order_by(MarketMovers.volume_spike.desc())
    
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
    scheduler.add_job(ipo_snapshot.update_upcoming_ipos, "interval", days=1)
    scheduler.add_job(signals_snapshot.detect_signals, "interval", hours=3)
    scheduler.add_job(market_snapshot.update_market_data, "interval", hours=1)
    scheduler.add_job(ai_insights_snapshot.generate_ai_insights_snapshot, "interval", hours=2)
    scheduler.start()

    if USE_DEV_ENDPOINT:
        dividend_snapshot.update_upcoming_dividendsForDevEnv()
        ipo_snapshot.update_upcoming_iposForDevEnv()
        signals_snapshot.detect_signalsForDevEnv()
        market_snapshot.update_market_dataForDevEnv()
        ai_insights_snapshot.generate_ai_insights_snapshotForDevEnv()
    else:
        dividend_snapshot.update_upcoming_dividends()
        ipo_snapshot.update_upcoming_ipos()
        signals_snapshot.detect_signals()
        market_snapshot.update_market_data()
        ai_insights_snapshot.generate_ai_insights_snapshot()

    app.run(host="0.0.0.0", port=5001, debug=False)
