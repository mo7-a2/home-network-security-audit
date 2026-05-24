#!/usr/bin/env python3
"""
Formatters - Different output formats for jokes
"""

import json
from typing import List, Dict, Any


class BaseFormatter:
    """Base formatter class."""

    def format(self, jokes: List[Dict[str, Any]]) -> str:
        """
        Format jokes for output.

        Args:
            jokes: List of joke dictionaries

        Returns:
            Formatted output string
        """
        raise NotImplementedError


class TextFormatter(BaseFormatter):
    """Plain text formatter."""

    def format(self, jokes: List[Dict[str, Any]]) -> str:
        """Format jokes as plain text."""
        output = []

        for i, joke in enumerate(jokes, 1):
            output.append(f"\nJoke {i}:")
            output.append(f"--------")
            output.append(joke["text"])
            output.append(f"Category: {joke.get('category', 'N/A')}")
            output.append(f"Source: {joke.get('source', 'N/A')}")

        return "\n".join(output)


class JSONFormatter(BaseFormatter):
    """JSON formatter."""

    def format(self, jokes: List[Dict[str, Any]]) -> str:
        """Format jokes as JSON."""
        data = {
            "jokes": jokes,
            "count": len(jokes),
        }
        return json.dumps(data, indent=2)


class CLIFormatter(BaseFormatter):
    """Beautiful CLI formatter with box drawing."""

    def format(self, jokes: List[Dict[str, Any]]) -> str:
        """Format jokes with beautiful CLI box."""
        output = []

        for i, joke in enumerate(jokes, 1):
            # Box header
            output.append("┌" + "─" * 45 + "┐")
            output.append("│" + "Random Joke Generator".center(45) + "│")
            output.append("└" + "─" * 45 + "┘")
            output.append("")

            # Joke content
            output.append(f"Type: {joke.get('type', 'N/A').capitalize()}")
            output.append(f"Category: {joke.get('category', 'N/A')}")
            output.append("")

            # Wrap joke text
            joke_text = joke["text"]
            wrapped = self._wrap_text(joke_text, 43)
            for line in wrapped:
                output.append(line)

            output.append("")
            output.append(f"Source: {joke.get('source', 'N/A')}")
            output.append("")

            if i < len(jokes):
                output.append("")

        return "\n".join(output)

    @staticmethod
    def _wrap_text(text: str, width: int) -> List[str]:
        """Wrap text to specified width."""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            if len(" ".join(current_line + [word])) <= width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines
