"""
Usage: python main.py TSLA
python main.py TSLA --company "Tesla, Inc."

Environment variables:
REDDIT_CLIENT_ID
REDDIT_CLIENT_SECRET
REDDIT_USER_AGENT
EDGAR_USER_AGENT
"""

import argparse
import os
import statistics
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv

from storage import *

from web_scrapers.edgar_scraper import get_edgar_filings
# from web_scrapers.reddit_scraper import get_reddit_mentions
from web_scrapers.stocktwits_scraper import get_stocktwits_mentions

load_dotenv()

# needs ticker but optional company name for edgar
def run(ticker: str, company_name: str | None):
    # start database and log time
    init_db()
    now = datetime.now(timezone.utc).isoformat()
    ticker = ticker.upper()

    all_mentions = []

    # load hits from edgar
    edgar_user_agent = os.getenv("EDGAR_USER_AGENT")
    # make sure user agent enabled
    if edgar_user_agent and company_name:
        try: 
            # gets hits and appends them to all_mentions
            edgar_hits = get_edgar_filings(company_name, edgar_user_agent)
            print (f"[edgar] fetched {len(edgar_hits)} filings")
            for m in edgar_hits:
                m["source_type"] = "edgar"
                all_mentions.append(m)
        except Exception as e:
            print(f"[edgar] error: {e}")
    else:
        print("[edgar] skipped (set EDGAR_USER_AGENT and pass --company to enable)")


    # #load hits from reddit
    # reddit_id = os.getenv("REDDIT_CLIENT_ID")
    # reddit_secret = os.getenv("REDDIT_CLIENT_SECRET")
    # reddit_user_agent = os.getenv("REDDIT_USER_AGENT")
    # # gets all credientials and makes sure they are all valid 
    # if reddit_id and reddit_secret and reddit_user_agent:
    #     try:
    #         # gets hits and appends them to all_mentions
    #         reddit_hits = get_reddit_mentions(ticker, reddit_id, reddit_secret, reddit_user_agent)
    #         print(f"[reddt] fetched {len(reddit_hits)} filings")
    #         for m in reddit_hits:
    #             m["source_type"] = "reddit"
    #             all_mentions.append(m)
    #     except Exception as e:
    #         print(f"[reddit] error: {e}")
    # else:
    #     print("[reddit] skipped (missing REDDIT_CLIENT_ID / SECRET / USER_AGENT)")

    # load hits from stocktwits
    # no credientials needed
    try: 
        # gets hits and appends
        st_hits = get_stocktwits_mentions(ticker)
        print (f"[stocktwits] fetched {len(st_hits)} filings")
        for m in st_hits:
            m["source_type"] = "stocktwits"
            all_mentions.append(m)
    except Exception as e:
        print(f"[stocktwits] error: {e}")

    # store
    inserted, skipped = 0, 0
    # modify database with ticker and fetched_at; scrapers should have filled in all other columns
    with get_conn() as conn:
        for m in all_mentions:
            m["ticker"] = ticker
            m["fetched_at"] = now
            m.setdefault("title", None)
            m.setdefault("text", None)
            m.setdefault("author", None)
            m.setdefault("url", None)
            m.setdefault("raw_json", None)
            if insert_mention(conn, m):
                inserted += 1
            else:
                skipped += 1
        
        recent_1h = count_recent_mentions(conn, ticker, hours=1)
        recent_24h = count_recent_mentions(conn, ticker, hours=24)
        baseline_counts = count_recent_mentions(conn, ticker, hours=720)

    #show summary
    print(f"{ticker} summary")
    print(f"new mentions inserted: {inserted} (skipped {skipped} duplicates)")
    print(f"mentions in last 1h: {recent_1h}")
    print(f"mentions in last 24h: {recent_24h}")
    #print(f"mentions in last 30d: {baseline_counts}")

    # look at zscore to see if volume fluctuates
    z = compute_volume_zscore(recent_24h, baseline_counts)
    print(f"volume z-score vs 30-day daily basetline: {z:.2f}" if z is not None else "not enough history yet for a baseline")

    if z is not None and z >= 3:
        print(">>> VOLUME SPIKE DETECTED -- consider triggering Pipeline B <<<<")

    return z

# compare 1 day's counts to average daily counts and the standard deviation to find zscore
def compute_volume_zscore(current_count: int, baseline_counts: list[int]):
    # makes sure there are at least 5 days worth of data
    if len(baseline_counts) < 5:
        return None
    mean = statistics.mean(baseline_counts)
    stdev = statistics.pstdev(baseline_counts)
    if stdev == 0: 
        return (current_count-mean) / stdev
    
if __name__ == "__main__":
    # parses arguements to allow compatibility with cron; only ran if main is not imported
    parser = argparse.ArgumentParser(description="pipeline A: structured news/filing/social ingestion")
    parser.add_argument("ticker", help="stock ticker symbol, e.g. TSLA")
    parser.add_argument("--company", help='full company name for EDGAR search, e.g. "Tesla, Inc."', default=None)
    args = parser.parse_args()
 
    run(args.ticker, args.company)
