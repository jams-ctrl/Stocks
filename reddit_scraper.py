import praw 
from datetime import datetime, timezone

DEFAULT_SUBREDDITS = ["stocks", "wallstreetbets", "investing", "stockMarket"]

def get_reddit_mentions(ticker: str, client_id: str, client_secret:str, user_agent: str,subreddits=None,limit_per_sub: int=25):
    subreddits = subreddits or DEFAULT_SUBREDDITS

    # use praw library to scrape reddit; client-side stuff will be imported in .env file
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )
    reddit.read_only = True

    results = []
    query = str(ticker)

    for sub_name in subreddits:
        # for each subreddit search for the stock symbol and log various details about the post 
        # in a try-catch to stop errors
        try: 
            selected_subreddit = reddit.subreddit(sub_name)
            for post in selected_subreddit.search(query, sort="new", time_filer="day"):
                results.append(
                    {
                        "external_id": post.id,
                        "source_name": sub_name,
                        "author": str(post.author) if post.author else "[deleted]",
                        # for debugging purposes
                        "url": f"https://reddit.com{post.permalink}",
                        "title": post.title, 
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
            print (f"[reddit] warning: subreddit=[sub_name] error={e}")
            continue
    return results
