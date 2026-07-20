import pandas as pd
import re
import urllib.request
import io

# get the ticker symbols, the full names, and the common names of all the companies and put them in a list for easy conversion
def get_sp500_lists():
    # go to wikipedia apge
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    with urllib.request.urlopen(req) as response:
        html_str = response.read().decode('utf-8')
        clean_buffer = io.StringIO(html_str)
        tables = pd.read_html(clean_buffer, match="Symbol")

    # take correct table from webpage
    df = tables[0]

    # extract tickers
    tickers = df["Symbol"].tolist()

    # extract full names
    full_names = df["Security"].tolist()

    # generate common names by removing corporate jargon
    common_names = []
    for name in full_names:
        clean = re.sub(r',?\s+(Inc\.|Corp\.|Co\.|Ltd\.|plc|Corporation|Incorporated|& Co\.|Company|\.com,?\s*Inc\.)\s*$', '', name, flags=re.IGNORECASE)
        # removes stock share classes (class a, b, c...)
        clean = re.sub(r',?\s+(Class [A-Z])\s*$', '', clean, flags=re.IGNORECASE)
        # removes hanging commas
        clean = re.sub(r',\s*$', '', clean).strip()
        common_names.append(clean)


    return tickers, full_names, common_names

#execute function to get 3 parallel lists
tickers, full_names, common_names = get_sp500_lists()

# build case-insensitive lookup dicts once at load time
# maps lowercase name to index in the original (correctly-cased) lists
ticker_lookup = {t.lower(): i for i, t in enumerate(tickers)}
full_name_lookup = {n.lower(): i for i, n in enumerate(full_names)}
common_name_lookup = {n.lower(): i for i, n in enumerate(common_names)}

def get_other_names(name):
    key = name.strip().lower()

    if key in ticker_lookup:
        index = ticker_lookup[key]
        return ("ticker", full_names[index], common_names[index])
    elif key in full_name_lookup:
        index = full_name_lookup[key]
        return ("full_names", tickers[index], common_names[index])
    elif key in common_name_lookup:
        index = common_name_lookup[key]
        return ("common_names", tickers[index], full_names[index])
    else:
        return None

#print to debug
# print(f"Total elements loaded: {len(tickers)}")
# print("Tickers array sample: ", tickers[:5])
# print("Full names array sample: ", full_names[:5])
# print("Common names array sample:", common_names[:5])

def get_top_50():
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
    return tickers
