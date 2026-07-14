import requests
from datetime import datetime,timezone

STOCKTWITS_URL =  "https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json"

def get_stocktwits_mentions(ticker: str, company_name=None):
    # define url based on ticker symbol or company name 
    url = STOCKTWITS_URL.format(symbol=ticker) if company_name is None else STOCKTWITS_URL.format(symbol=company_name)
    headers = {"User-Agent": "Mozilla/5.0 (compatible; stock-news-bot/1.0)"}
    resp = requests.get(url,headers=headers, timeout=15)

    # handle errors
    if resp.status_code == 429:
        print("[stocktwits] error: rate limited, skipping this run")
        return []
    if resp.status_code != 200:
        print(f"[stocktwits] error: status={resp.status_code}")
        return []
    
    # get info from stocktwits and handle None 
    data = resp.json()
    # only returns the most recent 30 messages for a symbol, consider using since if want more comprehensive list 
    messages = data.get("messages", [])

    results = []
    for msg in messages:
        sentiment=None
        entities = msg.get("entities") or {}
        sentiment_obj = entities.get("sentiment")
        if sentiment_obj:
            # get the "bullish" or "bearish" tag from stocktwits as a form of authenticity
            sentiment = sentiment_obj.get("basic")

        # pulls out object so can be accessed easily
        user = msg.get("user", {})
        # prepare for sqlite database
        results.append(
            {
                # stop duplicates
                "external_id": str(msg.get("id")),
                "source_name": "stocktwits",
                "author": user.get("username"),
                # for debugging purposes
                "url": f"https://stocktwits.com/{user.get('username')}/message/{msg.get('id')}",
                "title": None, 
                # gives body text of post 
                "text": msg.get("body","")[:2000],
                "published_at": _to_iso(msg.get("created_at")),
                # important, can be used to evaluate authenticity and impact
                "raw_json": str({
                    "sentiment": sentiment,
                    "follower_count": user.get("followers"),
                    "is_official": user.get("official", False),
                }),
            }
        )
    return results

# change time to correct isoformat for easy modification and uniformity 
def _to_iso(created_at):
    if not created_at:
        return datetime.now(timezone.utc).isoformat()
    try:
        # the format for stocktwits is "2026-07-09T14:23:00Z"
        return datetime.strptime(created_at,  "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).isoformat()
    except ValueError:
        return datetime.now(timezone.utc).isoformat()
