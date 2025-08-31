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

Open `http://localhost:5000` and the dashboard will load the latest 20 stories
asynchronously. Use the controls at the top to choose the number of stories
(20–100) and sorting method (latest, trending, top, or oldest). The **Refresh**
button pulls a fresh snapshot, and **Load More** dynamically appends additional
stories without reloading the page. Each story is de‑duplicated, summarised via
an open‑source NLP model, scored for relevance/bias/trendiness, and includes
clickable references and perspective notes.

### Twitter trends

Trending topics from Twitter can be blended into the feed. Provide Twitter API
credentials via environment variables. The agent will exchange the key and
secret for a bearer token when needed.

```bash
export TWITTER_API_KEY=pSE413xxsPnvqoHpBdKBiQwFd
export TWITTER_API_SECRET=qJKaTw6jGPHdRnxoYfRwGmL8VrTlw5Q4qFPA4jJagyebIgmOTP
# optional pre-generated token
# export TWITTER_BEARER_TOKEN=YOUR_TOKEN
```

`TwitterTrendsFetcher` in `newsfeed/twitter_feed.py` crawls the trending, news,
and entertainment tabs and converts the top topics into `Story` objects.

## Deployment on Vercel

The repository includes a minimal `vercel.json` and an `api/index.py` entrypoint
so the Flask app can run as a serverless function on [Vercel](https://vercel.com).

1. Push this repository to GitHub.
2. In the Vercel dashboard choose **New Project** → **Import Git Repository** and
   select your fork.
3. Keep the default settings; Vercel will install the dependencies from
   `requirements.txt` and build the Python function defined in `api/index.py`.
4. After the deployment finishes, Vercel provides a URL such as
   `https://your-project-name.vercel.app` where the news feed is available.

## Generating Briefs via CLI

`generate_brief.py` prints a markdown summary of the top stories and can be
scheduled via cron to run before the 13:00 IST delivery time:

```bash
PYTHONPATH=. python generate_brief.py --limit 20 > brief.md
```

The generated `brief.md` can then be emailed or posted to Slack.
