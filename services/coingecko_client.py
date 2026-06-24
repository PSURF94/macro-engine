import requests


BASE = "https://api.coingecko.com/api/v3"


def coletar_cripto() -> dict:
    try:
        r = requests.get(f"{BASE}/global", timeout=10)
        r.raise_for_status()
        data = r.json()["data"]
        btc_dom = data["market_cap_percentage"].get("btc", 0)
        total_mcap = data["total_market_cap"].get("usd", 0)

        r2 = requests.get(
            f"{BASE}/simple/price",
            params={"ids": "bitcoin", "vs_currencies": "usd", "include_24hr_change": "true"},
            timeout=10,
        )
        r2.raise_for_status()
        btc_data = r2.json().get("bitcoin", {})

        return {
            "btc_preco": btc_data.get("usd"),
            "btc_var_24h_pct": round(btc_data.get("usd_24h_change", 0), 3),
            "btc_dominancia_pct": round(btc_dom, 2),
            "total_market_cap_usd": total_mcap,
        }
    except Exception as e:
        return {"erro": str(e)}
