import requests

_HEADERS = {"User-Agent": "Mozilla/5.0"}
_BASE = "https://query1.finance.yahoo.com/v8/finance/chart"

SIMBOLOS_YAHOO = {
    "ouro":   "GC=F",       # Gold futures — mais líquido que spot
    "eurusd": "EURUSD=X",   # EUR/USD spot
}


def _fetch(symbol: str) -> dict | None:
    try:
        r = requests.get(
            f"{_BASE}/{symbol}",
            headers=_HEADERS,
            params={"interval": "1h", "range": "2d"},
            timeout=10,
        )
        if not r.ok:
            return None
        result = r.json()["chart"]["result"]
        if not result:
            return None
        data = result[0]
        meta = data["meta"]
        closes = data["indicators"]["quote"][0].get("close", [])
        closes = [c for c in closes if c is not None]
        if not closes:
            return None

        preco     = closes[-1]
        preco_1h  = closes[-2] if len(closes) >= 2 else None
        abertura  = meta.get("chartPreviousClose") or meta.get("regularMarketPreviousClose")
        max_dia   = meta.get("regularMarketDayHigh")
        min_dia   = meta.get("regularMarketDayLow")

        var_dia = round((preco - abertura) / abertura * 100, 3) if abertura else None
        var_1h  = round((preco - preco_1h) / preco_1h * 100, 3) if preco_1h else None

        return {
            "symbol":      symbol,
            "preco":       round(preco, 4),
            "var_dia_pct": var_dia,
            "var_dia_abs": round(preco - abertura, 4) if abertura else None,
            "abertura":    round(abertura, 4) if abertura else None,
            "max_dia":     round(max_dia, 4) if max_dia else None,
            "min_dia":     round(min_dia, 4) if min_dia else None,
            "var_1h_pct":  var_1h,
        }
    except Exception:
        return None


def coletar_precos_yahoo() -> dict:
    resultado = {}
    for nome, symbol in SIMBOLOS_YAHOO.items():
        dado = _fetch(symbol)
        resultado[nome] = dado if dado else {"erro": "sem dado"}
    return resultado
