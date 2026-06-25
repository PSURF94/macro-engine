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
    "https://www.forexlive.com/feed/news",                       # breaking news macro/forex — mais rápido
    "https://www.forexlive.com/feed/centralbank",                # Fed, ECB, BOJ — decisões e falas
    "https://www.rttnews.com/RSS/EconomicNews.xml",              # dados econômicos publicados — RTTNews
    "https://www.cnbc.com/id/10000664/device/rss/rss.html",     # mercados EUA — CNBC
]

RSS_KEYWORDS = {
    # política monetária
    "fed", "fomc", "rate cut", "rate hike", "powell", "ecb", "lagarde",
    "boj", "rba", "boe", "central bank", "interest rate", "monetary",
    # macro dados
    "cpi", "pce", "inflation", "payroll", "nonfarm", "gdp", "unemployment",
    "jobless", "claims", "retail", "manufacturing", "pmi", "ifo", "confidence",
    # mercados e liquidez
    "treasury", "yield", "spread", "liquidity", "m2", "balance sheet",
    "recession", "default", "debt", "deficit",
    # câmbio e risco
    "dollar", "euro", "dxy", "risk-off", "risk-on",
    # geopolítica
    "war", "sanction", "tariff", "trade",
}

FRED_SERIES = {
    "fed_funds":    "FEDFUNDS",
    "treasury_2y":  "DGS2",
    "treasury_10y": "DGS10",
    "m2":           "M2SL",
    "fed_balance":  "WALCL",
}
