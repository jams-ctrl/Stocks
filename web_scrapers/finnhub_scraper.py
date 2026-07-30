import websocket
import finnhub
import json
from datetime import datetime, timezone

# sets client and API key 
finnhub_client = finnhub.Client(api_key="d9lll11r01qomrv3q1i0d9lll11r01qomrv3q1ig")
# global variable for 1-recieve only
received = False

# shows current price of stock
def get_price(ticker: str):
    quote = finnhub_client.quote(ticker)
    # quote returns: {'c': current price, 'h': high, 'l': low, 'o': open, 'pc': prev close, 't': unix timestamp}
    return quote['c']

# shows market status of the US stock exchange
def market_status():
    return finnhub_client.market_status(exchange='US')

# returns all companies that reside in the same country and are in the same industry
def get_neighbours(ticker:str):
    # index 1 over because returns company itself in first slot 
    return finnhub_client.company_peers(ticker)[1:]

# gives summary of all insider trades 
def insider_trades(ticker):
    return finnhub_client.stock_insider_sentiment(ticker, '2021-01-01', '2022-03-01')

# get summary of all financials from 10-k filing of SEC such as assets, liabilities, ...
def financials(ticker):
    return finnhub_client.financials_reported(symbol=ticker, freq='annual')["data"][0]['report']["bs"]
#,finnhub_client.company_earnings('TSLA', limit=5)[0]["surprise"]

# converts date to 
def to_iso (date):
    return datetime.fromtimestamp(date, tz=timezone.utc).isoformat()[:10]

# gets mentions from various news outlets supported by finnhub and puts it in correct form to be loaded to the mentions.py database by main.py
def get_finnhub_mentions(ticker: str, company_name=None):
    msg = finnhub_client.company_news(ticker, _from="2025-12-01", to="2026-06-10")
    results = []
    for article in msg:
        # most common sources: Yahoo (majority), Bezinga, SeekingAlpha, CNBC, ChartMill
        results.append(
            {
                # stop duplicates
                "external_id": article["id"],
                "source_name": article["source"],
                "author": None,
                # for debugging purposes
                "url": article["url"],
                "title": article["headline"], 
                # gives body text of post 
                "text": article["summary"],
                "published_at": to_iso(article["datetime"]),
                # important, can be used to evaluate authenticity and impact
                "raw_json": None, 
                "follower_count": None,    
            }
        )
        print(to_iso(article["datetime"]))
    return results

if __name__ == "__main__":
    ticker = "AAPL"
    # print(get_finnhub_mentions(ticker))
    # print(get_price(ticker))
    # print(get_neighbours(ticker))
    print(financials(ticker))
    print(insider_trades(ticker))
