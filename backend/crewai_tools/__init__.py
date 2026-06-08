import os
import requests


class SerperDevTool:
    def __init__(self) -> None:
        self.name = "SerperDevTool"
        self.api_key = os.getenv("SERPER_API_KEY")
        self.search_url = "https://google.serper.dev/search"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-API-KEY": self.api_key or "",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "SerperDevTool/1.0",
            }
        )

    def search(self, query: str) -> list[dict[str, str]]:
        if not self.api_key:
            return [
                {
                    "title": "SerperSearch fallback result",
                    "url": "https://serper.dev",
                    "snippet": "SERPER_API_KEY is not configured. Install the key to use Serper search.",
                }
            ]

        payload = {"q": query, "gl": "us", "hl": "en"}
        response = self.session.post(self.search_url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        results: list[dict[str, str]] = []
        for item in data.get("organic", [])[:5]:
            results.append(
                {
                    "title": item.get("title", "SerperSearch result"),
                    "url": item.get("link", item.get("url", "")),
                    "snippet": item.get("snippet", item.get("description", "")) or "No summary available.",
                }
            )

        if not results:
            results.append(
                {
                    "title": "No search results",
                    "url": "",
                    "snippet": "SerperSearch returned no organic results for this query.",
                }
            )

        return results

    def __repr__(self) -> str:
        return f"<SerperDevTool name={self.name!r}>"
