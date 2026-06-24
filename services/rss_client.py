import feedparser
from datetime import datetime, timezone, timedelta
from config import RSS_FEEDS, RSS_KEYWORDS


def headlines_recentes(janela_horas: int = 2) -> list[dict]:
    corte = datetime.now(timezone.utc) - timedelta(hours=janela_horas)
    encontrados = []

    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                publicado = entry.get("published_parsed")
                if publicado:
                    pub_dt = datetime(*publicado[:6], tzinfo=timezone.utc)
                    if pub_dt < corte:
                        continue
                titulo = entry.get("title", "").lower()
                resumo = entry.get("summary", "").lower()
                texto = titulo + " " + resumo
                if any(kw in texto for kw in RSS_KEYWORDS):
                    encontrados.append({
                        "titulo": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "publicado": entry.get("published", ""),
                        "fonte": feed.feed.get("title", url),
                    })
        except Exception:
            continue

    return encontrados


def tem_breaking_news() -> bool:
    return len(headlines_recentes(janela_horas=1)) > 0
