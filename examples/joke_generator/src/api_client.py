#!/usr/bin/env python3
"""
API Client - Handles HTTP requests to joke APIs
"""

import requests
import json
from typing import Dict, Any, Optional


class APIClient:
    """HTTP client for making API requests."""

    def __init__(self, timeout: int = 10):
        """
        Initialize API client.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Random-Joke-Generator/1.0",
            "Accept": "application/json",
        })

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make GET request to API endpoint.

        Args:
            url: API endpoint URL
            params: Query parameters

        Returns:
            JSON response as dictionary

        Raises:
            requests.exceptions.RequestException: If request fails
        """
        response = self.session.get(
            url,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()

        # Handle different response types
        if "application/json" in response.headers.get("content-type", ""):
            return response.json()
        else:
            # For plain text responses (like ICanHazDadJoke)
            return {"joke": response.text}

    def close(self):
        """Close the session."""
        self.session.close()
