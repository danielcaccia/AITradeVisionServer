import traceback

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

    def generate_ai_insights_snapshot(self):
        print("Generating AI Picks snapshot...")
        print("============================================")
        
        now = datetime.now()

        for symbol in TICKERS:
            print(f"Processing AI insight for symbol: {symbol}")

            try:
                result = self.fetcher.fetch_news_for_symbol(symbol)

                for article in result["articles"]:
                    title = article.get("title", "")
                    url = article.get("url", "")

                    exists = AiInsight.select().where(
                        (AiInsight.symbol == symbol) &
                        (AiInsight.title == title)
                    ).exists()

                    if exists:
                        continue

                    summary = summarize_article(article.get("content") or article.get("description") or "")

                    AiInsight.create(
                        symbol=symbol,
                        title=title,
                        description=article.get("description"),
                        url=url,
                        published_at=article.get("publishedAt"),
                        sentiment=article.get("sentiment"),
                        summary=summary,
                        source=article.get("source", {}).get("name", ""),
                        created_at=now
                    )

            except Exception as e:
                print(traceback.format_exc())
                print(f"❌ Error on {symbol}: {e}")

        print("============================================")
        print("AI Picks snapshot generated.")

    def generate_ai_insights_snapshotForDevEnv(self):
        print("Running in DEV MODE: Generating AI Picks snapshot...")
        print("============================================")
        
        now = datetime.now()

        for symbol in ['AAPL', 'DIS', 'TSLA', 'VZ']:
            print(f"Processing AI insight for symbol: {symbol}")

            try:
                result = self.fetcher.fetch_news_for_symbol(symbol)

                for article in result["articles"]:
                    title = article.get("title", "")
                    url = article.get("url", "")

                    exists = AiInsight.select().where(
                        (AiInsight.symbol == symbol) &
                        (AiInsight.title == title)
                    ).exists()

                    if exists:
                        continue

                    summary = summarize_article(article.get("content") or article.get("description") or "")

                    AiInsight.create(
                        symbol=symbol,
                        title=title,
                        description=article.get("description"),
                        url=url,
                        published_at=article.get("publishedAt"),
                        sentiment=article.get("sentiment"),
                        summary=summary,
                        source=article.get("source", {}).get("name", ""),
                        created_at=now
                    )

            except Exception as e:
                print(traceback.format_exc())
                print(f"❌ Error on {symbol}: {e}")

        print("============================================")
        print("AI Picks snapshot generated.")
