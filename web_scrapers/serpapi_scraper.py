import serpapi
import json
import sys
import os
# go up one parent folder
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from company_name_manager import get_top
# go down a parent folder
sys.path.remove(parent_dir)

tickers = get_top()
for ticker in tickers:
  # define API key
  client = serpapi.Client(api_key="ee20eacab05ccd6f05fae6a3cecdc8f0b6a432a7cb164569e73a74b059c90a8e")
  results = client.search({
    # serach using correct ticker
    "engine": "google_trends",
    "q": f"{ticker}",
    "date": "today 12-m",
    "tz": "420",
    "data_type": "TIMESERIES"
  })
  # search is returned as dict - debug message
  interest_over_time = results["interest_over_time"]
  print(f"{ticker} appended")

  # Save the dictionary to a file in google_trends folder
  with open(f"google_trends/{ticker}.json", "w") as file:
      json.dump(interest_over_time, file, indent=4)