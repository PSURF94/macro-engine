import requests
from datetime import date
from config import TRADING_ECO_KEY


BASE = "https://api.tradingeconomics.com"


def calendario_hoje() -> list[dict]:
    hoje = date.today().isoformat()
    try:
        r = requests.get(
            f"{BASE}/calendar",
            params={
                "c": TRADING_ECO_KEY,
                "d1": hoje,
                "d2": hoje,
                "country": "united states",
                "f": "json",
            },
            timeout=15,
        )
        r.raise_for_status()
        eventos = r.json()
        return [
            {
                "hora": e.get("Date", ""),
                "evento": e.get("Event", ""),
                "anterior": e.get("Previous"),
                "consenso": e.get("Forecast"),
                "actual": e.get("Actual"),
                "importancia": e.get("Importance", 1),
            }
            for e in eventos
        ]
    except Exception as e:
        return [{"erro": str(e)}]
