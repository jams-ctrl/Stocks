import pandas as pd
import re
import urllib.request
import io

# get the ticker symbols, the full names, and the common names of all the companies and put them in a list for easy conversion
def get_sp500_lists():
    # go to wikipedia page
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
        "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "GOOG", "META", "TSLA", "BRK-B", "AVGO",
        "JPM", "V", "MA", "WMT", "UNH", "XOM", "JNJ", "PG", "HD", "COST",
        "KO", "PEP", "BAC", "NFLX", "ADBE", "CRM", "ORCL", "CSCO", "INTC", "AMD",
        "QCOM", "IBM", "MCD", "SBUX", "NKE", "DIS", "CVX", "GS", "AXP", "BA",
        "F", "GM", "VZ", "T", "PYPL", "TGT", "LOW", "FDX", "UPS", "MMM",
        "EBAY", "TXN", "INTU", "AMAT", "MU", "ADI", "LRCX", "KLAC", "SNPS", "CDNS",
        "PANW", "CRWD", "FTNT", "NXPI", "MCHP", "ON", "EA", "CTSH", "ABT", "PFE",
        "MRK", "LLY", "ABBV", "BMY", "CVS", "CI", "ELV", "HUM", "MDT", "ISRG",
        "GILD", "AMGN", "REGN", "VRTX", "WFC", "C", "MS", "SCHW", "BLK", "SPGI",
        "MCO", "ICE", "CME", "COF", "USB", "PNC", "TFC", "BNY", "MET", "PRU"
    ]
    return tickers
