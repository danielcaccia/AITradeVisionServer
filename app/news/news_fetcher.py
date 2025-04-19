import requests
import os
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_ORG_API_KEY")
NEWS_BASE_URL = "https://newsapi.org/v2/everything"

class NewsFetcher:
    def __init__(self):
        self.session = requests.Session()

    def fetch_news(self, query, sort_by="publishedAt", page_size=20):
        params = {
            "q": query,
            "language": "en",
            "sortBy": sort_by,
            "pageSize": page_size,
            "apiKey": NEWS_API_KEY
        }

        response = self.session.get(NEWS_BASE_URL, params=params)
        if response.status_code != 200:
            print(f"NewsAPI error: {response.status_code} - {response.text}")
            return []

        return response.json().get("articles", [])

    def fetch_top_combined_news(self, query="stock OR finance OR investing", top_n=5):
        recent_news = self.fetch_news(query, "publishedAt")
        popular_news = self.fetch_news(query, "popularity")
        relevant_news = self.fetch_news(query, "relevancy")

        combined = {}

        def normalize_title(title):
            return title.lower().strip()

        def add_or_update(article, category):
            key = normalize_title(article["title"])
            if key not in combined:
                combined[key] = {
                    "article": article,
                    "score": 0,
                    "sources": set()
                }
            combined[key]["score"] += 1
            combined[key]["sources"].add(category)

        for article in recent_news:
            add_or_update(article, "recent")
        for article in popular_news:
            add_or_update(article, "popular")
        for article in relevant_news:
            add_or_update(article, "relevant")

        sorted_articles = sorted(
            combined.values(),
            key=lambda x: (x["score"], x["article"].get("publishedAt", "")),
            reverse=True
        )

        return [item["article"] for item in sorted_articles[:top_n]]

    def fetch_news_for_symbol(self, symbol, top_n=5):
        query = f'"{symbol}" stock'
        return self.fetch_top_combined_news(query=query, top_n=top_n)
