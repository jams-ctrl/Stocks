import requests
from datetime import datetime, timezone, timedelta

EDGAR_FTS_URL = "https://efts.sec.gov/LATEST/search-index"

# high-signal filing types, expand if need more coverage
DEFAULT_FORMS = ["8-K", "4", "SC 13D", "SC 13G","NT 10-Q","NT 10-K","144"]

# days-back- days back to extend search by
def get_edgar_filings(company_name:str, user_agent:str, forms=None, days_back: int=200):
    # note company_name is exact or partial company name as registered with the SEC - E.g "Tesla, Inc."; ticker symbols are unreliable
    # forms - list of form types to filter on - defaults to DEFAULT_FORMS

    forms = forms or DEFAULT_FORMS
    headers = {"User-Agent": user_agent}

    results = []
    # makes seperate API call per form
    for form in forms:
        # filter keywords in forms
        params = {
            "q": f"{company_name}",
            "forms": form, 
            "dateRange": "custom",
            "startdt": _days_ago(days_back), 
            "enddt": _today(),

        }
        resp = requests.get(EDGAR_FTS_URL, params=params, headers=headers, timeout=15)
        # handle error
        if resp.status_code != 200:
            print(f"[edgar] error: form={form} status={resp.status_code}")
            continue
        data=resp.json()
        # per form, cycle though all hits
        hits = data.get("hits",{}).get("hits",[])
        # handle elasticsearch response shape
        for hit in hits:
            src = hit.get("_source", {})
            # the external_id in this case, used to dedup
            accession_no = hit.get("_id", "")
            # central index key - unique company ID
            cik = (src.get("ciks") or None)[0]
            filed_at = src.get("file_date")
            filing_url = _build_filing_url(cik, accession_no)
            # put data in format of sqlite table
            results.append(
                {
                    # stop duplicates
                    "external_id": accession_no,
                    "source_name": form,
                    "author": src.get("display_names", [company_name])[0],
                    # for debugging purposes
                    "url": filing_url,
                    "title": f"{form} filing - {src.get('display_names', [company_name])[0]}", 
                    # gives body text of post 
                    "text": src.get("file_description",""),
                    "published_at": _to_iso(filed_at),
                    # important, can be used to evaluate authenticity and impact
                    "raw_json": str(src),
                }
            )

    return results

def _build_filing_url(cik, accession_no):
    # builds the full url to that page
    if not cik or not accession_no:
        return None
    return f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_no.replace('-', '')}"

# date helpers to standardize dates into y-m-d
def _days_ago(n):
    return (datetime.now(timezone.utc) - timedelta(days=n)).strftime("%Y-%m-%d")

def _today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def _to_iso(date_str):
    if not date_str:
        return datetime.now(timezone.utc).isoformat()
    try:
        # the format for stocktwits is "2026-07-09T14:23:00Z"
        return datetime.strptime(date_str,  "%Y-%m-%d").replace(tzinfo=timezone.utc).isoformat()
    except ValueError:
        return datetime.now(timezone.utc).isoformat()
