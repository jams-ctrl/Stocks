import sqlite3
from contextlib import contextmanager  
from datetime import datetime, timedelta, timezone

DB_PATH = "mentions.db"

# create table with said columns
SCHEMA = """
CREATE TABLE IF NOT EXISTS mentions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    ticker TEXT NOT NULL, 
    source_type TEXT NOT NULL, 
    source_name TEXT, 
    author TEXT, 
    external_id TEXT NOT NULL, 
    url TEXT,
    Title TEXT,
    text TEXT, 
    published_at TEXT NOT NULL, 
    fetched_at TEXT NOT NULL, 
    raw_json TEXT, 
    UNIQUE(source_type, external_id)
);

CREATE INDEX IF NOT EXISTS idx_mentions_ticker_time
    ON mentions(ticker, published_at);
"""
# above: create "shortcut" that sqlite can jump to to quickly navigate table and yield output

@contextmanager
# open connection with database using context manager
def get_conn(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    # categorize each value as a dictionary-like row-column pair
    conn.row_factory = sqlite3.Row
    try: 
        yield conn
        conn.commit()
    finally: 
        conn.close

def init_db(db_path: str = DB_PATH):
    with get_conn(db_path) as conn:
        # runs schema listed above
        conn.executescript(SCHEMA)

# inserts new row into table
def insert_mention(conn, mention:dict) -> bool:
    try :
        # pass mention dict as parameter to get easy access to inside values
        conn.execute(
            """
            INSERT INTO mentions (ticker, source_type, source_name, author, external_id, url, title, text, published_at, fetched_at, raw_json)
            VALUES (:ticker, :source_type, :source_name, :author, :external_id, :url, :title, :text,:published_at, :fetched_at, :raw_json)
            """,
            mention,
        )
        return True
    except sqlite3.IntegrityError:
        # if the row is repetative (external_id is not unique)
        return False
    
def count_recent_mentions(conn, ticker:str, hours:int) -> int:
    # count recent mentions of stock, cutoff at an hour
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    # index helps a lot with fast searching
    row = conn.execute(
        "SELECT COUNT(*) AS c FROM mentions WHERE ticker = ? AND published_at >= ?", (ticker, since),
    ).fetchone()
    return row["c"]

def daily_mention_counts(conn, ticker: str, days:int) -> list[int]:
    since = (datetime.now (timezone.utc) - timedelta(days=days)).date()
    # chops ISO timestamp into just date section with days as lowest value
    # adds one to count for every day stock is mentioned
    rows = conn.execute(
        """
        SELECT substr(published_at, 1, 10) AS day, COUNT(*) AS c 
        FROM mentions
        WHERE ticker = ? AND published_at >= ?
        GROUP BY day
        ORDER BY day ASC
        """,
        (ticker, since.isoformat()),
    ).fetchall()
    return [r["c"] for r in rows]
