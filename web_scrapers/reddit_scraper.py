import praw 
from datetime import datetime, timezone

# list of subreddits, expand if want more coverage
DEFAULT_SUBREDDITS = ["stocks", "wallstreetbets", "investing", "stockMarket"]

def get_reddit_mentions(ticker: str, client_id: str, client_secret:str, user_agent: str,subreddits=None,company_name=None, limit_per_sub: int=25):
    subreddits = subreddits or DEFAULT_SUBREDDITS

    # use praw library to scrape reddit; client-side stuff will be imported in .env file
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )
    reddit.read_only = True

    results = []
    # use ticker to search 
    query = ticker 

    for sub_name in subreddits:
        # for each subreddit search for the stock symbol and log various details about the post 
        try: 
            selected_subreddit = reddit.subreddit(sub_name)
            # capped at 25 results to not dig into old threads
            for post in selected_subreddit.search(query, sort="new", time_filer="day"):
                # put data in format of sqlite table
                results.append(
                    {
                        # stop duplicates
                        "external_id": post.id,
                        "source_name": sub_name,
                        "author": str(post.author) if post.author else "[deleted]",
                        # for debugging purposes
                        "url": f"https://reddit.com{post.permalink}",
                        "title": post.title, 
                        # gives body text of post 
                        "text": (post.selftext or "")[:2000],
                        "published_at": datetime.fromtimestamp(post.created_utc, tz=timezone.utc).isoformat(),
                        # important, can be used to evaluate authenticity and impact
                        "raw_json": str({
                            "score": post.score,
                            "num_comments": post.num_comment,
                            "upvote_ratio": post.upvote_ratio,
                        })
                    }
                )
        except Exception as e:
        # catches potential errors
            print (f"[reddit] warning: subreddit=[sub_name] error={e}")
            continue
    return results
