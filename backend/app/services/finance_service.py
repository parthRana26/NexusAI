import requests
from app.core.config import settings

class FinanceService:
    def __init__(self):
        self.api_key = settings.ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"

    def get_stock_quote(self, symbol: str):
        """
        Get real-time stock quote from Alpha Vantage.
        """
        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            quote = data.get("Global Quote", {})
            return {
                "symbol": quote.get("01. symbol"),
                "price": quote.get("05. price"),
                "change": quote.get("09. change"),
                "change_percent": quote.get("10. change percent")
            }
        except Exception as e:
            print(f"Finance Service Error: {e}")
            return {}

    def search_ticker(self, keywords: str):
        """
        Search for stock tickers.
        """
        try:
            params = {
                "function": "SYMBOL_SEARCH",
                "keywords": keywords,
                "apikey": self.api_key
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            return data.get("bestMatches", [])
        except Exception as e:
            print(f"Finance Search Error: {e}")
            return []

finance_service = FinanceService()
