# Given the top 50 tech companies, scrapes nasdaq (consider switching to yahoo finance) for stock data and downloads it 
# in the form of .csv files
import requests
import pandas as pd
import os
import sys
from datetime import datetime, timezone
# go up one parent folder
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
# since went up one parent folder all function calls are made from the invisible "parent-folder" - must change in prediction.py to use the right filepath
from company_name_manager import get_top_50
# go down 1 parent folder
sys.path.remove(parent_dir)

# top 50 tech companies as seen in company_name_manager
tickers = get_top_50()

for company in tickers:
    # go to this link (nasdaq API) presenting as a browser and get data in between a range of dates
    past = "2021-07-02"
    present = str(datetime.now(timezone.utc))[:11]
    url = "https://api.nasdaq.com/api/quote/"+ company + f"/historical?assetclass=stocks&fromdate={past}&todate={present}&limit=1260"
    headers = {"User-Agent": "Mozilla/5.0"}

    # get table values and turn into dataFrame -> use pandas library
    data = requests.get(url, headers=headers).json()
    if data is not None:
        rows = data['data']['tradesTable']['rows']
    df = pd.DataFrame(rows)
    # make path to navigate different folders
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "..", "stock_data", f"{company}_5yr_data.csv")
    # turn dataFrame into csv and download into certain path
    df.to_csv(csv_path, index=False)
