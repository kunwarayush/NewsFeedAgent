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
