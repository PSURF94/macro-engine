import requests
import time
from datetime import date, datetime, timezone, timedelta
from config import FINNHUB_API_KEY

BASE    = "https://finnhub.io/api/v1"
HEADERS = {"X-Finnhub-Token": FINNHUB_API_KEY}

# Símbolos Finnhub — free tier, sem delay
SIMBOLOS_QUOTE = {
    "sp500":  "SPY",              # ETF S&P 500 — real-time
    "nasdaq": "QQQ",              # ETF Nasdaq — real-time
    "dxy":    "UUP",              # ETF proxy DXY (Invesco DB USD Bullish)
    "vix":    "VIXY",             # ETF proxy VIX (ProShares VIX Short-Term)
    "ouro":   "OANDA:XAU_USD",   # Ouro spot via Finnhub Forex
    "btc":    "BINANCE:BTCUSDT", # BTC via Binance
}

ENDPOINTS_CANDLE = {
    "sp500":  ("stock",  "SPY"),
    "nasdaq": ("stock",  "QQQ"),
    "dxy":    ("stock",  "UUP"),
    "vix":    ("stock",  "VIXY"),
    "ouro":   ("forex",  "OANDA:XAU_USD"),
    "btc":    ("crypto", "BINANCE:BTCUSDT"),
}


def _quote(symbol: str) -> dict | None:
    try:
        r = requests.get(f"{BASE}/quote", headers=HEADERS, params={"symbol": symbol}, timeout=8)
        r.raise_for_status()
        d = r.json()
        if d.get("c", 0) == 0:
            return None
        return d
    except Exception:
        return None


def _candle_1h(tipo: str, symbol: str) -> tuple[float | None, float | None]:
    """Retorna (preco_atual, preco_1h_atras) via candles de 60 min."""
    agora = int(time.time())
    de    = agora - 7200  # 2h para garantir 2 candles
    try:
        r = requests.get(
            f"{BASE}/{tipo}/candle",
            headers=HEADERS,
            params={"symbol": symbol, "resolution": "60", "from": de, "to": agora},
            timeout=8,
        )
        r.raise_for_status()
        d = r.json()
        if d.get("s") != "ok" or not d.get("c"):
            return None, None
        closes = d["c"]
        if len(closes) < 2:
            return closes[-1], None
        return closes[-1], closes[-2]
    except Exception:
        return None, None


def coletar_precos() -> dict:
    resultado = {}

    for nome, symbol in SIMBOLOS_QUOTE.items():
        q = _quote(symbol)
        if not q:
            resultado[nome] = {"erro": "sem dado"}
            continue

        tipo, sym_candle = ENDPOINTS_CANDLE[nome]
        atual_1h, ant_1h = _candle_1h(tipo, sym_candle)

        var_1h = None
        if atual_1h and ant_1h and ant_1h != 0:
            var_1h = round((atual_1h - ant_1h) / ant_1h * 100, 3)

        resultado[nome] = {
            "symbol":      symbol,
            "preco":       round(q["c"], 4),
            "var_dia_pct": round(q.get("dp", 0), 3),
            "var_dia_abs": round(q.get("d", 0), 4),
            "abertura":    round(q.get("o", 0), 4),
            "max_dia":     round(q.get("h", 0), 4),
            "min_dia":     round(q.get("l", 0), 4),
            "var_1h_pct":  var_1h,
        }

    return resultado


# ── Calendário econômico ──────────────────────────────────────────────────────

IMPACTO_MAP = {"low": 1, "medium": 2, "high": 3}


def calendario_hoje() -> list[dict]:
    hoje = date.today().isoformat()
    try:
        r = requests.get(
            f"{BASE}/calendar/economic",
            headers=HEADERS,
            params={"from": hoje, "to": hoje},
            timeout=10,
        )
        r.raise_for_status()
        eventos = r.json().get("economicCalendar", [])

        resultado = []
        for e in eventos:
            if e.get("country", "").upper() != "US":
                continue
            resultado.append({
                "hora":       e.get("time", ""),
                "evento":     e.get("event", ""),
                "anterior":   e.get("prev"),
                "consenso":   e.get("estimate"),
                "actual":     e.get("actual"),
                "importancia": IMPACTO_MAP.get(str(e.get("impact", "")).lower(), 1),
                "unidade":    e.get("unit", ""),
            })

        return sorted(resultado, key=lambda x: x["hora"])
    except Exception as e:
        return [{"erro": str(e)}]


def novos_dados_calendario() -> list[dict]:
    """Retorna apenas eventos que já têm actual publicado nas últimas 2h."""
    todos  = calendario_hoje()
    corte  = datetime.now(timezone.utc) - timedelta(hours=2)
    resultado = []

    for e in todos:
        if e.get("actual") is None:
            continue
        try:
            pub = datetime.fromisoformat(e["hora"].replace(" ", "T"))
            if pub.tzinfo is None:
                pub = pub.replace(tzinfo=timezone.utc)
            if pub >= corte:
                resultado.append(e)
        except Exception:
            resultado.append(e)

    return resultado
