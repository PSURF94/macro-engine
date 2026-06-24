import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def enviar(texto: str, parse_mode: str = "HTML") -> bool:
    MAX = 4096
    partes = [texto[i:i+MAX] for i in range(0, len(texto), MAX)]
    ok = True
    for parte in partes:
        r = requests.post(
            f"{BASE}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": parte, "parse_mode": parse_mode},
            timeout=10,
        )
        if not r.ok:
            ok = False
    return ok
