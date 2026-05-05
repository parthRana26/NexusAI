import wikipedia

class WikiService:
    @staticmethod
    def search(query: str, limit: int = 3):
        """
        Search Wikipedia for information.
        """
        try:
            results = wikipedia.search(query)
            data = []
            for title in results[:limit]:
                try:
                    summary = wikipedia.summary(title, sentences=3)
                    page = wikipedia.page(title)
                    data.append({
                        "title": title,
                        "summary": summary,
                        "url": page.url
                    })
                except Exception:
                    continue
            return data
        except Exception as e:
            print(f"Wiki Service Error: {e}")
            return []

wiki_service = WikiService()
