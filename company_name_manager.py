import pandas as pd
import re
import requests
import io

# get the ticker symbols, the full names, and the common names of all the companies and put them in a list for easy conversion
def get_sp500_lists():
    # go to wikipedia page
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    response = requests.get(url, headers=headers)
    # debug error
    response.raise_for_status
    html_str = response.text
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

    def clean_company_name(name):
        clean = name.strip()
        
        # remove parenthesies
        clean = re.sub(r'\s*\((?:Class\s+[A-Z]|The|[A-Z])\)\s*', ' ', clean, flags=re.IGNORECASE)
        
        # remove legal suffixes (with or without trailing period), possibly repeated
        suffix_pattern = (
            r',?\s+('
            r'Inc\.?|Corp\.?|Co\.?|Ltd\.?|plc|Corporation|Incorporated|'
            r'& Co\.?|Company|\.com,?\s*Inc\.?'
            r')\s*$'
        )
        
        # remove stacked suffixes (e.g X.corp.inc)
        prev = None
        while prev != clean:
            prev = clean
            clean = re.sub(suffix_pattern, '', clean, flags=re.IGNORECASE).strip()
            clean = re.sub(r',?\s+Class\s+[A-Z]\s*$', '', clean, flags=re.IGNORECASE).strip()
        
        # handle leading and trailing "the"
        clean = re.sub(r'^The\s+', '', clean, flags=re.IGNORECASE)
        clean = re.sub(r',?\s*The\s*$', '', clean, flags=re.IGNORECASE)

        # remove jargon like "technologies"
        clean = re.sub("technologies",'',clean,flags=re.IGNORECASE)
        
        # collapse double spaces and trailing commas/whitespace
        clean = re.sub(r'\s{2,}', ' ', clean)
        clean = re.sub(r',\s*$', '', clean).strip()
        
        return clean

    common_names = [clean_company_name(name) for name in full_names]
    #print(common_names)

    return tickers, full_names, common_names

#execute function to get 3 parallel lists
tickers, full_names, common_names = get_sp500_lists()

# build case-insensitive lookup dicts once at load time
# maps lowercase name to index in the original (correctly-cased) lists
ticker_lookup = {t.lower(): i for i, t in enumerate(tickers)}
full_name_lookup = {n.lower(): i for i, n in enumerate(full_names)}
common_name_lookup = {n.lower(): i for i, n in enumerate(common_names)}

def get_other_names(name):
    # given a name, assigns it a type and returns the 2 other matching types
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
#print("Full names array sample: ", full_names)
#print("Common names array sample:", common_names)

def get_top():
    # top 100 most popular companies as deemed by me
    tickers = [
        "NVDA",   # NVIDIA Corporation
        "AAPL",   # Apple Inc.
        "MSFT",   # Microsoft Corporation
        "GOOGL",  # Alphabet Inc. (Class A)
        "GOOG",   # Alphabet Inc. (Class C)
        "AMZN",   # Amazon.com Inc.
        "META",   # Meta Platforms Inc.
        "TSLA",   # Tesla Inc.
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
        "ZS",     # Zscaler Inc.
        "DDOG",   # Datadog Inc.
        "NXPI",   # NXP Semiconductors N.V.
        "MCHP",   # Microchip Technology Inc.
        "ON",     # ON Semiconductor Corporation
        "EA",     # Electronic Arts Inc.
        "CTSH",   # Cognizant Technology Solutions Corp.
        "BRK-B",  # Berkshire Hathaway Inc. (Class B)
        "AVGO",   # Broadcom Inc.
        "JPM",    # JPMorgan Chase & Co.
        "V",      # Visa Inc.
        "MA",     # Mastercard Inc.
        "WMT",    # Walmart Inc.
        "UNH",    # UnitedHealth Group Inc.
        "XOM",    # ExxonMobil Corporation
        "JNJ",    # Johnson & Johnson
        "PG",     # Procter & Gamble Co.
        "HD",     # Home Depot Inc.
        "KO",     # Coca-Cola Company
        "BAC",    # Bank of America Corporation
        "CRM",    # Salesforce Inc.
        "ORCL",   # Oracle Corporation
        "IBM",    # International Business Machines Corporation
        "MCD",    # McDonald's Corporation
        "NKE",    # Nike Inc.
        "DIS",    # Walt Disney Company
        "CVX",    # Chevron Corporation
        "GS",     # Goldman Sachs Group Inc.
        "AXP",    # American Express Company
        "BA",     # Boeing Company
        "F",      # Ford Motor Company
        "GM",     # General Motors Company
        "VZ",     # Verizon Communications Inc.
        "T",      # AT&T Inc.
        "TGT",    # Target Corporation
        "LOW",    # Lowe's Companies Inc.
        "FDX",    # FedEx Corporation
        "UPS",    # United Parcel Service Inc.
        "MMM",    # 3M Company
        "EBAY",   # eBay Inc.
        "ABT",    # Abbott Laboratories
        "PFE",    # Pfizer Inc.
        "MRK",    # Merck & Co. Inc.
        "LLY",    # Eli Lilly and Company
        "ABBV",   # AbbVie Inc.
        "BMY",    # Bristol-Myers Squibb Company
        "CVS",    # CVS Health Corporation
        "CI",     # Cigna Group
        "ELV",    # Elevance Health Inc.
        "HUM",    # Humana Inc.
        "MDT",    # Medtronic plc
        "ISRG",   # Intuitive Surgical Inc.
        "GILD",   # Gilead Sciences Inc.
        "AMGN",   # Amgen Inc.
        "REGN",   # Regeneron Pharmaceuticals Inc.
        "VRTX",   # Vertex Pharmaceuticals Inc.
        "WFC",    # Wells Fargo & Company
        "C",      # Citigroup Inc.
        "MS",     # Morgan Stanley
        "SCHW",   # Charles Schwab Corporation
        "BLK",    # BlackRock Inc.
        "SPGI",   # S&P Global Inc.
        "MCO",    # Moody's Corporation
        "ICE",    # Intercontinental Exchange Inc.
        "CME",    # CME Group Inc.
        "COF",    # Capital One Financial Corporation
        "USB",    # U.S. Bancorp
        "PNC",    # PNC Financial Services Group Inc.
        "TFC",    # Truist Financial Corporation
        "BNY",    # BNY Mellon
        "MET",    # MetLife Inc.
        "PRU",    # Prudential Financial Inc.
    ]
    return tickers
