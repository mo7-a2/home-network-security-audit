#!/usr/bin/env python3
"""
Random Joke Generator - Main entry point
Fetches jokes from multiple free APIs with a beautiful CLI interface
"""

import argparse
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.joke_fetcher import JokeFetcher
from src.formatters import CLIFormatter, JSONFormatter, TextFormatter

__version__ = "1.0.0"


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Random Joke Generator - Fetch jokes from multiple APIs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Get a random joke
  python main.py --api jokeapi --safe      # Get safe joke from JokeAPI
  python main.py --category programming   # Get programming joke
  python main.py --count 5 --format json   # Get 5 jokes as JSON
  python main.py --interactive             # Start interactive mode
        """,
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        "--api",
        choices=["jokeapi", "official", "dadjoke", "chucknorris", "random"],
        default="random",
        help="Choose the API source (default: random)",
    )

    parser.add_argument(
        "--category", type=str, help="Filter jokes by category"
    )

    parser.add_argument(
        "--count",
        type=int,
        default=1,
        metavar="N",
        help="Number of jokes to fetch (default: 1)",
    )

    parser.add_argument(
        "--safe",
        action="store_true",
        help="Enable safe mode (exclude NSFW content)",
    )

    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Start interactive CLI mode",
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output",
    )

    return parser


def get_formatter(format_type: str):
    """Get appropriate formatter based on format type."""
    formatters = {
        "text": TextFormatter(),
        "json": JSONFormatter(),
        "cli": CLIFormatter(),
    }
    return formatters.get(format_type, CLIFormatter())


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        fetcher = JokeFetcher(verbose=args.verbose)

        if args.interactive:
            run_interactive_mode(fetcher)
        else:
            run_single_mode(fetcher, args)

    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def run_single_mode(fetcher: JokeFetcher, args):
    """Run single joke fetch mode."""
    formatter = get_formatter(args.format)

    jokes = fetcher.fetch_jokes(
        api=args.api,
        count=args.count,
        category=args.category,
        safe=args.safe,
    )

    if not jokes:
        print("Failed to fetch jokes from all available APIs.", file=sys.stderr)
        sys.exit(1)

    output = formatter.format(jokes)
    print(output)


def run_interactive_mode(fetcher: JokeFetcher):
    """Run interactive CLI mode."""
    formatter = CLIFormatter()

    print("\n" + "=" * 50)
    print("  Random Joke Generator - Interactive Mode")
    print("=" * 50 + "\n")

    while True:
        print("\nOptions:")
        print("  1. Get a random joke")
        print("  2. Get joke by category")
        print("  3. Get multiple jokes")
        print("  4. Choose API source")
        print("  5. Exit\n")

        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            jokes = fetcher.fetch_jokes(count=1)
            if jokes:
                print("\n" + formatter.format(jokes))

        elif choice == "2":
            category = input("Enter category: ").strip()
            jokes = fetcher.fetch_jokes(category=category, count=1)
            if jokes:
                print("\n" + formatter.format(jokes))

        elif choice == "3":
            count_str = input("How many jokes? (1-10): ").strip()
            try:
                count = min(int(count_str), 10)
                jokes = fetcher.fetch_jokes(count=count)
                if jokes:
                    print("\n" + formatter.format(jokes))
            except ValueError:
                print("Invalid number!")

        elif choice == "4":
            print("\nAvailable APIs:")
            print("  1. jokeapi")
            print("  2. official")
            print("  3. dadjoke")
            print("  4. chucknorris")
            api_choice = input("Choose API (1-4): ").strip()
            api_map = {"1": "jokeapi", "2": "official", "3": "dadjoke", "4": "chucknorris"}
            selected_api = api_map.get(api_choice, "random")
            jokes = fetcher.fetch_jokes(api=selected_api, count=1)
            if jokes:
                print("\n" + formatter.format(jokes))

        elif choice == "5":
            print("\nThank you for using Random Joke Generator!")
            break

        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
