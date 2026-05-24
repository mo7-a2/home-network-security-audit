# Random Joke Generator

A Python application that fetches random jokes from multiple free APIs with a beautiful CLI interface.

## Features

- **Multiple API Sources**: JokeAPI, Official Joke API, Dad Jokes, Chuck Norris APIs
- **Category Support**: Filter jokes by category
- **Safe Mode**: Exclude NSFW content
- **Output Formats**: Text and JSON
- **Interactive CLI**: User-friendly command-line interface
- **Error Handling**: Robust error handling with API fallbacks

## Supported APIs

1. **JokeAPI** - Wide range of categories
2. **Official Joke API** - Simple and reliable
3. **ICanHazDadJoke** - Dad jokes only
4. **Chuck Norris API** - Chuck Norris jokes

## Installation

```bash
cd examples/joke_generator
pip install -r requirements.txt
```

## Usage

### Get a Random Joke

```bash
python main.py
```

### Get Joke from Specific API

```bash
python main.py --api jokeapi
python main.py --api official
python main.py --api dadjoke
python main.py --api chucknorris
```

### Get by Category

```bash
python main.py --category programming
python main.py --api official --category knock-knock
```

### Safe Mode

```bash
python main.py --safe
```

### Output Options

```bash
# Multiple jokes
python main.py --count 5

# JSON format
python main.py --count 3 --format json
```

### Interactive Mode

```bash
python main.py --interactive
```

### Help

```bash
python main.py --help
```

## Examples

### Example 1: Get a Random Safe Joke

```bash
$ python main.py --safe

┌─────────────────────────────────────────┐
│      Random Joke Generator              │
└─────────────────────────────────────────┘

Type: Single
Category: Programming

Why do programmers prefer dark mode?
Because light attracts bugs!

Source: Official Joke API
```

### Example 2: Get 5 Programming Jokes

```bash
python main.py --api jokeapi --category programming --count 5
```

### Example 3: Interactive Mode

```bash
python main.py --interactive
```

### Example 4: JSON Output

```bash
python main.py --count 3 --format json > jokes.json
```

## Project Structure

```
joke_generator/
├── main.py                 # Entry point
├── src/
│   ├── __init__.py
│   ├── api_client.py      # HTTP client
│   ├── joke_fetcher.py    # Joke fetching logic
│   └── formatters.py      # Output formatters
├── requirements.txt
└── README.md
```

## Performance

- Average Response Time: 200-500ms per joke
- Memory Usage: < 50MB

## Error Handling

- Connection timeouts (default: 10 seconds)
- Automatic fallback to alternative APIs
- Graceful handling of invalid categories
- Malformed response handling

## License

MIT License

## Author

Mohamed Anwar Abdelhay Mahdy
