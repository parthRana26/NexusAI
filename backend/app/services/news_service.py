import requests
from app.core.config import settings

class NewsService:
    def __init__(self):
        self.api_key = settings.GNEWS_API_KEY
        self.base_url = "https://gnews.io/api/v4/search"

    def get_news(self, query: str, limit: int = 5):
        """
        Get latest news using GNews API.
        """
        try:
            params = {
                "q": query,
                "token": self.api_key,
                "lang": "en",
                "max": limit
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            articles = []
            for art in data.get("articles", []):
                articles.append({
                    "title": art.get("title"),
                    "description": art.get("description"),
                    "url": art.get("url"),
                    "source": art.get("source", {}).get("name")
                })
            return articles
        except Exception as e:
            print(f"News Service Error: {e}")
            return []

news_service = NewsService()
