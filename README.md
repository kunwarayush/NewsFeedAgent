# NewsFeedAgent

Prototype implementation of an AI-powered news feed analyzer.

## Usage

Install dependencies:

```bash
python -m pip install -r requirements.txt  # or feedparser and Flask
```

Run the web interface:

```bash
PYTHONPATH=. python newsfeed/app.py
```

Access `http://localhost:5000/?limit=20` to view the top 20 stories. The limit can be any value between 1 and 100.
