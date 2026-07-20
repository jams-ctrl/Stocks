import requests
import pandas as pd
import os

# top 50 tech companies
tickers = [
    "NVDA",   # NVIDIA Corporation
    "AAPL",   # Apple Inc.
    "MSFT",   # Microsoft Corporation
    "GOOGL",  # Alphabet Inc. (Class A)
    "GOOG",   # Alphabet Inc. (Class C)
    "AMZN",   # Amazon.com Inc.
    "META",   # Meta Platforms Inc.
    "AVGO",   # Broadcom Inc.
    "TSLA",   # Tesla Inc.
    "ASML",   # ASML Holding N.V.
    "ADBE",   # Adobe Inc.
    "CSCO",   # Cisco Systems Inc.
    "INTC",   # Intel Corporation
    "AMD",    # Advanced Micro Devices Inc.
    "QCOM",   # Qualcomm Inc.
    "TXN",    # Texas Instruments Inc.
    "INTU",   # Intuit Inc.
    "AMAT",   # Applied Materials Inc.
    "MU",     # Micron Technology Inc.
    "ADI",    # Analog Devices Inc.
    "LRCX",   # Lam Research Corporation
    "KLAC",   # KLA Corporation
    "SNPS",   # Synopsys Inc.
    "CDNS",   # Cadence Design Systems Inc.
    "PANW",   # Palo Alto Networks Inc.
    "CRWD",   # CrowdStrike Holdings Inc.
    "FTNT",   # Fortinet Inc.
    "PYPL",   # PayPal Holdings Inc.
    "NFLX",   # Netflix Inc.
    "CMCSA",  # Comcast Corporation
    "PEP",    # PepsiCo Inc.
    "COST",   # Costco Wholesale Corporation
    "SBUX",   # Starbucks Corporation
    "MRVL",   # Marvell Technology Inc.
    "ADSK",   # Autodesk Inc.
    "WDAY",   # Workday Inc.
    "TEAM",   # Atlassian Corporation
    "ZS",     # Zscaler Inc.
    "DDOG",   # Datadog Inc.
    "MDB",    # MongoDB Inc.
    "SNOW",   # Snowflake Inc.
    "DOCU",   # DocuSign Inc.
    "OKTA",   # Okta Inc.
    "NXPI",   # NXP Semiconductors N.V.
    "MCHP",   # Microchip Technology Inc.
    "ON",     # ON Semiconductor Corporation
    "EA",     # Electronic Arts Inc.
    "ROKU",   # Roku Inc.
    "ZM",     # Zoom Communications Inc.
    "CTSH",   # Cognizant Technology Solutions Corp.
]

for company in tickers:
    # go to this link presenting as a browser
    url = "https://api.nasdaq.com/api/quote/"+ company + "/historical?assetclass=stocks&fromdate=2021-07-02&todate=2026-07-02&limit=1260"
    headers = {"User-Agent": "Mozilla/5.0"}

    # get table values and turn into dataFrame
    data = requests.get(url, headers=headers).json()
    if data is not None:
        rows = data['data']['tradesTable']['rows']
    df = pd.DataFrame(rows)
    # make path to navigate different folders
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "..", "stock_data", f"{company}_5yr_data.csv")
    # turn dataFrame into csv and download
    df.to_csv(csv_path, index=False)
