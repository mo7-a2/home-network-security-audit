#!/usr/bin/env python3
"""
Joke Fetcher - Main logic for fetching jokes from multiple APIs
"""

import random
from typing import List, Optional, Dict, Any
from src.api_client import APIClient


class JokeFetcher:
    """Main class for fetching and managing jokes."""

    APIS = {
        "jokeapi": {
            "url": "https://v2.jokeapi.dev/joke",
            "categories": ["Programming", "Miscellaneous", "Pun", "Spooky", "Christmas", "Dark"],
        },
        "official": {
            "url": "https://official-joke-api.appspot.com/jokes",
            "categories": ["general", "programming", "knock-knock"],
        },
        "dadjoke": {
            "url": "https://icanhazdadjoke.com",
            "categories": [],
        },
        "chucknorris": {
            "url": "https://api.chucknorris.io/jokes",
            "categories": ["animal", "career", "celebrity", "dev", "sport"],
        },
    }

    def __init__(self, timeout: int = 10, verbose: bool = False):
        """
        Initialize the joke fetcher.

        Args:
            timeout: Request timeout in seconds
            verbose: Enable verbose output
        """
        self.client = APIClient(timeout=timeout)
        self.verbose = verbose

    def fetch_jokes(
        self,
        api: str = "random",
        count: int = 1,
        category: Optional[str] = None,
        safe: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Fetch jokes from specified API.

        Args:
            api: API source (jokeapi, official, dadjoke, chucknorris, random)
            count: Number of jokes to fetch
            category: Category filter
            safe: Safe mode (exclude NSFW)

        Returns:
            List of joke dictionaries
        """
        if api == "random":
            api = random.choice(list(self.APIS.keys()))
            if self.verbose:
                print(f"Selected API: {api}")

        jokes = []
        apis_to_try = [api] if api in self.APIS else list(self.APIS.keys())

        for current_api in apis_to_try:
            try:
                jokes = self._fetch_from_api(
                    current_api, count, category, safe
                )
                if jokes:
                    break
            except Exception as e:
                if self.verbose:
                    print(f"Failed to fetch from {current_api}: {e}")
                continue

        return jokes

    def _fetch_from_api(
        self,
        api: str,
        count: int,
        category: Optional[str],
        safe: bool,
    ) -> List[Dict[str, Any]]:
        """
        Fetch jokes from a specific API.

        Args:
            api: API name
            count: Number of jokes
            category: Category filter
            safe: Safe mode

        Returns:
            List of jokes
        """
        if api == "jokeapi":
            return self._fetch_jokeapi(count, category, safe)
        elif api == "official":
            return self._fetch_official(count, category)
        elif api == "dadjoke":
            return self._fetch_dadjoke(count)
        elif api == "chucknorris":
            return self._fetch_chucknorris(count, category)
        return []

    def _fetch_jokeapi(
        self,
        count: int,
        category: Optional[str],
        safe: bool,
    ) -> List[Dict[str, Any]]:
        """Fetch from JokeAPI."""
        jokes = []
        category = category or "Any"
        safe_flag = "safe-mode" if safe else ""
        url = f"{self.APIS['jokeapi']['url']}/{category}?{safe_flag}"

        for _ in range(count):
            try:
                data = self.client.get(url)
                if data.get("type") == "twopart":
                    joke_text = f"{data['setup']}\n{data['delivery']}"
                else:
                    joke_text = data.get("joke", "")

                jokes.append({
                    "text": joke_text,
                    "category": data.get("category", "Miscellaneous"),
                    "type": data.get("type", "single"),
                    "source": "JokeAPI",
                })
            except Exception:
                continue

        return jokes

    def _fetch_official(
        self,
        count: int,
        category: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Fetch from Official Joke API."""
        jokes = []
        
        if category:
            url = f"{self.APIS['official']['url']}/{category}/random"
        else:
            url = f"{self.APIS['official']['url']}/random"

        for _ in range(count):
            try:
                data = self.client.get(url)
                if isinstance(data, list):
                    data = data[0]

                if data.get("type") == "twopart":
                    joke_text = f"{data['setup']}\n{data['punchline']}"
                else:
                    joke_text = data.get("joke", "")

                jokes.append({
                    "text": joke_text,
                    "category": data.get("type", "General"),
                    "type": data.get("type", "single"),
                    "source": "Official Joke API",
                })
            except Exception:
                continue

        return jokes

    def _fetch_dadjoke(self, count: int) -> List[Dict[str, Any]]:
        """Fetch from ICanHazDadJoke API."""
        jokes = []
        url = "https://icanhazdadjoke.com/"

        for _ in range(count):
            try:
                data = self.client.get(url)
                jokes.append({
                    "text": data.get("joke", ""),
                    "category": "Dad Joke",
                    "type": "single",
                    "source": "ICanHazDadJoke",
                })
            except Exception:
                continue

        return jokes

    def _fetch_chucknorris(
        self,
        count: int,
        category: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Fetch from Chuck Norris API."""
        jokes = []
        
        if category:
            url = f"{self.APIS['chucknorris']['url']}/random?category={category}"
        else:
            url = f"{self.APIS['chucknorris']['url']}/random"

        for _ in range(count):
            try:
                data = self.client.get(url)
                jokes.append({
                    "text": data.get("value", ""),
                    "category": data.get("categories", ["General"])[0] if data.get("categories") else "General",
                    "type": "single",
                    "source": "Chuck Norris API",
                })
            except Exception:
                continue

        return jokes
