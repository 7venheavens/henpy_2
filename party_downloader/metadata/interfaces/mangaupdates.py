from __future__ import annotations
import requests


class MangaUpdatesInterface:
    API_URLS = {
        "search": "https://api.mangaupdates.com/v1/series/search",
    }

    def _search_series(self, title: str) -> list[dict]:
        """Searches for a series by title and returns a list of results."""
        data = {
            "search": "one piece",
            "per_page": 10,
        }
        response = requests.post(url=self.API_URLS["search"], data=data)
        print(response.__dict__)
        response.raise_for_status()
        return response.json()["results"]


if __name__ == "__main__":
    mu = MangaUpdatesInterface()
    print(mu._search_series("one piece"))
