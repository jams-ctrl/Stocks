import requests
import json

symbol = "AAPL"

url = f"https://api-gw-prd.stocktwits.com/api-middleware/external/sentiment/v2/{symbol}/detail"

headers = {"User-Agent": "Mozilla/5.0 (compatible; stock-news-bot/1.0)"}
response = requests.get(url,headers=headers, timeout=15)

# data = response.json()
# print(data)
print(response.status_code)
print(response.headers.get("Content-Type"))
print(response.text[:500])