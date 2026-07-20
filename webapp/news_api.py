import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
import sys

import requests
from dotenv import load_dotenv

import sys
import os

from storage import init_db, get_conn, insert_mention

load_dotenv()

NEWSAPI_URL = "https://newsapi.org/v2/everything"
# use a manual source-authority list to assign authority to sources
SOURCE_AUTHORITY = {
    "reuters": 5, 
    "bloomberg": 5, 
    "the-wall-street-journal": 5, 
    "financial-times": 5,
    "cnbc": 4, 
    "business-insider": 3, 
    "fortune": 3, 
    "the-verge": 2, 
    "techcrunch": 2, 
}
DEFAULT_AUTHORITY = 2 # by default, sources get modest authority

# page_size limits input
def get_news(query:str, api_key:str, page_size: int=20):
    params = {
        "q": query,
        "apiKey": api_key,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": page_size,
    }
    resp = requests.get(NEWSAPI_URL, params=params, timeout=15)

    if resp.status_code == 429:
        print("[newsapi] error: rate limited (100/day on free tier), skipping this run")
        return[]
    if resp.status_code != 200:
        print(f"[newsapi] error: status={resp.status_code} body={resp.text[:200]}")
        return []
    data = resp.json()
    return data.get("articles", [])

def to_mention(article:dict, ticker:str, fetched_at:str) -> dict | None:
    url = article.get("url")
    title = article.get("title")
    if not url or not title:
        return None
    
    source = article.get("source") or {}
    source_id = (source.get("id") or "").lower()
    source_name = source.get("name") or source_id or "unknown"
    authority = SOURCE_AUTHORITY.get(source_id, DEFAULT_AUTHORITY)

    #NewsAPI gives no unique id, so hash url for consistent dedup
    external_id = hashlib.sha256(url.encode("utf-8")).hexdigest()[:32]

    description = article.get("description") or ""
    text = f"{description}\n\n[source authority: {authority}/5]"

    return {
        "ticker": ticker, 
        "source_type": "newsapi", 
        "source_name": source_name, 
        "author": article.get("author"), 
        "external_id": external_id, 
        "url": url, 
        "title": title,
        "text": text, 
        "published_at": article.get("publishedAt") or fetched_at, 
        "fetched_at": fetched_at, 
        "raw_json": json.dumps(article),
        "follower_count": authority
    }

def run(ticker: str, company_name:str | None = None):
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        print("[newsapi] error: NEWSAPI_KEY not assigned in .env")
        return
    
    ticker = ticker.upper()
    query = company_name or ticker

    print(f"[newsapi] fetching articles for '{query}'...")
    articles = get_news(query, api_key)
    print (f"[newsapi] fetched {len(articles)} articles (note: free tier is 24hr delayed)")

    now = datetime.now(timezone.utc).isoformat()
    inserted, skipped = 0,0

    with get_conn() as conn:
        for article in articles:
            mention = to_mention(article, ticker, now)
            if mention is None:
                continue
            if insert_mention(conn, mention):
                inserted += 1
            else: 
                skipped += 1

    print(f"[newsapi] inserted {inserted} new items, skipped {skipped} duplicates")

if __name__ == "__main__":
    init_db()
    # parser = argparse.ArgumentParser(description="NewsAPI-based news investigation")
    # parser.add_argument("ticker", help="Stock ticker symbol, e.g. TSLA")
    # parser.add_argument("company", nargs="?", default = None, help='Company name to search for, e.g. "Tesla.Inc"')
    # args = parser.parse_args()

    # run(args.ticker, args.company)
    # go up one parent folder
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    # since went up one parent folder all function calls are made from the invisible "parent-folder" - must change in prediction.py to use the right filepath
    from company_name_converter import get_top_50
    
    tickers = get_top_50()
    
    for ticker in tickers:
        run(ticker)
