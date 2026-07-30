import websocket
import finnhub
import json

# sets client and API key 
finnhub_client = finnhub.Client(api_key="d9lll11r01qomrv3q1i0d9lll11r01qomrv3q1ig")
# global variable for 1-recieve only
received = False

# shows market status
#print(finnhub_client.market_status(exchange='US'))

#gets companies operating in same country and industry
#print(finnhub_client.company_peers('AAPL'))

# gives summary of all insider trades 
#print(finnhub_client.stock_insider_sentiment('AAPL', '2021-01-01', '2022-03-01'))

# get summary of all financials from 10-k filing of SEC such as assets, liabilities, ...
#print(finnhub_client.financials_reported(symbol='AAPL', freq='annual'))
print(finnhub_client.company_earnings('TSLA', limit=5))

# get company news for the past year 
# msg = finnhub_client.company_news('AAPL', _from="2025-06-01", to="2026-06-10")
# for article in msg:
#     print(article["source"]) # most common sources: Yahoo (majority), Bezinga, SeekingAlpha, CNBC, ChartMill, 


# shows final price of stock as a result of most recent trade - to be called repeatedly by html
def on_message(ws, message):
    global received

    if received:
        return
    
    msg = json.loads(message)
    if msg["type"] != "trade":
        return
    
    trade = msg["data"][0]
    print(trade)
    last_price = trade["p"]

    print(f"Last price is {last_price}")
    received=True

    ws.close()

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print('###Closed###')

def on_open(ws):
    ws.send('{"type":"subscribe","symbol":"AAPL"}')
    # ws.send('{"type":"subscribe","symbol":"AMZN"}')
    # ws.send('{"type":"subscribe","symbol":"BINANCE:BTCUSDT"}')
    # ws.send('{"type":"subscribe","symbol":"IC MARKETS:1"}')

if __name__ == "__main__":
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp("wss://ws.finnhub.io?token=d9lll11r01qomrv3q1i0d9lll11r01qomrv3q1ig", 
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                )
    ws.on_open = on_open 
    ws.run_forever()