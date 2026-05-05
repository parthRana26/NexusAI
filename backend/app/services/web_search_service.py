from tavily import TavilyClient
from app.core.config import settings

class WebSearchService:
    def __init__(self):
        self.client = TavilyClient(api_key=settings.TAVILY_API_KEY)

    def search(self, query: str, search_depth: str = "basic"):
        """
        Search the web using Tavily.
        """
        try:
            results = self.client.search(query=query, search_depth=search_depth)
            formatted_results = []
            for res in results.get("results", []):
                formatted_results.append({
                    "title": res.get("title"),
                    "url": res.get("url"),
                    "content": res.get("content")
                })
            return formatted_results
        except Exception as e:
            print(f"Web Search Error: {e}")
            return []

web_search_service = WebSearchService()
