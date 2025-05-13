import traceback
import yfinance as yf

from datetime import datetime

from app.persistence.models import AiInsight

from app.news.news_fetcher import NewsFetcher

from app.ai.nlp.sentiment_analyzer import SentimentAnalyzer
from app.ai.llm.summarizer import summarize_article

from app.finance.tickers_list import TICKERS

class AiInsightsSnapshot:
    def __init__(self):
        analyzer = SentimentAnalyzer()
        self.fetcher = NewsFetcher(analyzer)
    
    def get_volume_info(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            fast_info = ticker.fast_info
            hist = ticker.history(period="30d")

            current_volume = fast_info.get("last_volume")
            avg_volume = hist["Volume"].mean() if not hist.empty else None

            if current_volume and avg_volume:
                volume_ratio = round(current_volume / avg_volume, 2)
                return current_volume, avg_volume, volume_ratio
            
        except Exception as e:
            print(traceback.format_exc())
            print(f"Volume error for {symbol}: {e}")

        return None, None, None
    
    def generate_ai_insights_snapshot(self):
        print("Generating AI Picks snapshot...")
        print("============================================")
        
        now = datetime.now()

        for symbol in TICKERS:
            print(f"Processing AI insight for symbol: {symbol}")

            try:
                articles_result = self.fetcher.fetch_news_for_symbol(symbol)
                articles = articles_result["articles"]

                _, _, volume_ratio = self.get_volume_info(symbol)

                for idx, article in enumerate(articles):
                    title = article.get("title", "")
                    url = article.get("url", "")
                    published = article.get("publishedAt")

                    if AiInsight.select().where(
                        (AiInsight.symbol == symbol) &
                        (AiInsight.title == title)
                    ).exists():
                        continue

                    summary = summarize_article(
                        article.get("content") or article.get("description") or ""
                    )

                    sentiment = article.get("sentiment", {})
                    sentiment_score = float(sentiment.get("score", 0.0))

                    relevance_score = max(1.0 - (idx * 0.05), 0.0)

                    AiInsight.create(
                        symbol=symbol,
                        title=title,
                        url=url,
                        published_at=published,
                        sentiment_score=sentiment_score,
                        summary=summary,
                        source=article.get("source", {}).get("name", ""),
                        created_at=now,
                        relevance_score=relevance_score,
                        volume_ratio=volume_ratio
                    )

            except Exception as e:
                print(traceback.format_exc())
                print(f"Error on {symbol}: {e}")

        print("============================================")
        print("AI Picks snapshot generated.")

    def generate_ai_insights_snapshotForDevEnv(self):
        print("Running in DEV MODE: Generating AI Picks snapshot...")
        print("============================================")
        
        now = datetime.now()

        for symbol in ['AAPL', 'DIS', 'TSLA', 'VZ']:
            print(f"Processing AI insight for symbol: {symbol}")

            try:
                articles_result = self.fetcher.fetch_news_for_symbol(symbol)
                articles = articles_result["articles"]

                _, _, volume_ratio = self.get_volume_info(symbol)

                for idx, article in enumerate(articles):
                    title = article.get("title", "")
                    url = article.get("url", "")
                    published = article.get("publishedAt")

                    if AiInsight.select().where(
                        (AiInsight.symbol == symbol) &
                        (AiInsight.title == title)
                    ).exists():
                        continue

                    summary = summarize_article(
                        article.get("content") or article.get("description") or ""
                    )

                    sentiment = article.get("sentiment", {})
                    sentiment_score = float(sentiment.get("score", 0.0))

                    relevance_score = max(1.0 - (idx * 0.05), 0.0)

                    AiInsight.create(
                        symbol=symbol,
                        title=title,
                        url=url,
                        published_at=published,
                        sentiment_score=sentiment_score,
                        summary=summary,
                        source=article.get("source", {}).get("name", ""),
                        created_at=now,
                        relevance_score=relevance_score,
                        volume_ratio=volume_ratio
                    )

            except Exception as e:
                print(traceback.format_exc())
                print(f"Error on {symbol}: {e}")

        print("============================================")
        print("AI Picks snapshot generated.")
