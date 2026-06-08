import os
from typing import Any

import requests


class SerperSearch:
    SEARCH_URL = "https://google.serper.dev/search"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("SERPER_API_KEY")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-API-KEY": self.api_key or "",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "SerperSearchClient/1.0",
            }
        )

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        if not self.api_key:
            return [
                {
                    "title": "SerperSearch fallback result",
                    "url": "https://serper.dev",
                    "snippet": f"SERPER_API_KEY is not configured. Unable to run a real search for '{query}'.",
                }
            ]

        payload = {
            "q": query,
            "gl": "us",
            "hl": "en",
        }
        response = self.session.post(self.SEARCH_URL, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        results: list[dict[str, Any]] = []
        for item in data.get("organic", [])[:limit]:
            title = item.get("title", "SerperSearch result")
            url = item.get("link", item.get("url", ""))
            snippet = item.get("snippet", item.get("description", ""))
            results.append(
                {
                    "title": title,
                    "url": url,
                    "snippet": snippet or "No summary available.",
                }
            )

        if not results:
            results.append(
                {
                    "title": "No search results",
                    "url": "",
                    "snippet": "SerperSearch returned no results for this query.",
                }
            )

        return results
