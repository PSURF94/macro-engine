from services.rss_client import headlines_recentes
from services.finnhub_client import novos_dados_calendario


LIMIARES = {
    "dxy":    0.5,   # % em 1h
    "btc":    3.0,   # % em 1h
    "sp500":  1.0,   # % em 1h
    "nasdaq": 1.2,   # % em 1h
    "ouro":   0.8,   # % em 1h
}


def detectar_eventos(precos: dict) -> list[dict]:
    eventos = []

    for ativo, limiar in LIMIARES.items():
        dados = precos.get(ativo, {})
        if not dados or "erro" in dados:
            continue
        var = abs(dados.get("var_1h_pct", 0) or 0)
        if var >= limiar:
            direcao = "alta" if dados["var_1h_pct"] > 0 else "queda"
            eventos.append({
                "tipo": "movimento_anormal",
                "ativo": ativo,
                "var_pct": dados["var_1h_pct"],
                "descricao": f"Movimento anormal: {ativo.upper()} {direcao} {var:.2f}% em 1h",
            })

    headlines = headlines_recentes(janela_horas=1)
    for h in headlines[:5]:
        eventos.append({
            "tipo": "breaking_news",
            "descricao": h["titulo"],
            "fonte": h["fonte"],
            "link": h["link"],
        })

    for e in novos_dados_calendario():
        if e.get("importancia", 1) >= 3:
            consenso = e.get("consenso")
            actual   = e.get("actual")
            if consenso is not None and actual is not None and actual != consenso:
                eventos.append({
                    "tipo":     "dado_calendario",
                    "evento":   e["evento"],
                    "actual":   actual,
                    "consenso": consenso,
                    "anterior": e.get("anterior"),
                    "descricao": f"{e['evento']}: real {actual} vs consenso {consenso}",
                })

    return eventos


def ha_gatilho(precos: dict) -> bool:
    return len(detectar_eventos(precos)) > 0
