import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]    # mesmo chat_id do Hermes
FRED_API_KEY       = os.environ["FRED_API_KEY"]
FINNHUB_API_KEY    = os.environ["FINNHUB_API_KEY"]
CEREBRAS_API_KEY   = os.environ["CEREBRAS_API_KEY"]
CEREBRAS_MODEL     = "gpt-oss-120b"

RSS_FEEDS = [
    "https://feeds.reuters.com/reuters/businessNews",
    "https://www.cnbc.com/id/10000664/device/rss/rss.html",
]

RSS_KEYWORDS = {
    "fed", "fomc", "rate cut", "rate hike", "cpi", "inflation",
    "payroll", "gdp", "recession", "default", "bank", "war",
    "sanction", "liquidity", "treasury", "yield", "powell",
}

FRED_SERIES = {
    "fed_funds":    "FEDFUNDS",
    "treasury_2y":  "DGS2",
    "treasury_10y": "DGS10",
    "m2":           "M2SL",
    "fed_balance":  "WALCL",
}
