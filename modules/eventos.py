from services.rss_client import headlines_recentes
from services.finnhub_client import novos_dados_calendario


LIMIARES = {
    "dxy":    0.5,   # % em 1h — regime filter
    "btc":    3.0,   # % em 1h
    "sp500":  1.0,   # % em 1h — regime filter
    "nasdaq": 1.2,   # % em 1h
    "ouro":   0.8,   # % em 1h
    "eurusd": 0.4,   # % em 1h
}


def _detectar_divergencia_eur_ouro(precos: dict) -> dict | None:
    """
    EUR e Ouro normalmente andam juntos (ambos inversos ao DXY).
    Quando divergem, o sinal nao e sobre USD — e algo especifico.
    Decorrelacoes com mais de 0.5% no dia geram um evento.
    """
    eur  = precos.get("eurusd", {})
    ouro = precos.get("ouro", {})

    if not eur or not ouro or "erro" in eur or "erro" in ouro:
        return None

    var_eur  = eur.get("var_dia_pct", 0) or 0
    var_ouro = ouro.get("var_dia_pct", 0) or 0

    # dispara apenas quando os dois estao em direcoes opostas com magnitude relevante
    sinais_opostos = (var_eur * var_ouro) < 0
    magnitude_ok   = abs(var_eur) >= 0.5 and abs(var_ouro) >= 0.5

    if not sinais_opostos or not magnitude_ok:
        return None

    if var_ouro > 0 and var_eur < 0:
        leitura = "RISCO EUROPEU ou GEOPOLITICO"
        acao    = "Long Ouro — evitar EUR/USD"
    elif var_eur > 0 and var_ouro < 0:
        leitura = "RISK-ON PURO — sem catalisa de medo"
        acao    = "Long EUR/USD — Ouro sem suporte"
    else:
        leitura = "DIVERGENCIA — aguardar confirmacao"
        acao    = "Nao operar os dois na mesma direcao"

    return {
        "tipo":       "divergencia_eur_ouro",
        "var_eur":    var_eur,
        "var_ouro":   var_ouro,
        "leitura":    leitura,
        "acao":       acao,
        "descricao":  (
            f"Divergencia EUR/Ouro: EUR/USD {var_eur:+.2f}% vs Ouro {var_ouro:+.2f}% | "
            f"{leitura} | {acao}"
        ),
    }


def detectar_eventos(precos: dict) -> list[dict]:
    eventos = []

    # movimentos anormais por ativo
    for ativo, limiar in LIMIARES.items():
        dados = precos.get(ativo, {})
        if not dados or "erro" in dados:
            continue
        var = abs(dados.get("var_1h_pct", 0) or 0)
        if var >= limiar:
            direcao = "alta" if dados["var_1h_pct"] > 0 else "queda"
            eventos.append({
                "tipo":      "movimento_anormal",
                "ativo":     ativo,
                "var_pct":   dados["var_1h_pct"],
                "descricao": f"Movimento anormal: {ativo.upper()} {direcao} {var:.2f}% em 1h",
            })

    # divergencia EUR vs Ouro
    divergencia = _detectar_divergencia_eur_ouro(precos)
    if divergencia:
        eventos.append(divergencia)

    # breaking news
    headlines = headlines_recentes(janela_horas=1)
    for h in headlines[:5]:
        eventos.append({
            "tipo":      "breaking_news",
            "descricao": h["titulo"],
            "fonte":     h["fonte"],
            "link":      h["link"],
        })

    # dados economicos publicados
    for e in novos_dados_calendario():
        if e.get("importancia", 1) >= 3:
            consenso = e.get("consenso")
            actual   = e.get("actual")
            if consenso is not None and actual is not None and actual != consenso:
                eventos.append({
                    "tipo":      "dado_calendario",
                    "evento":    e["evento"],
                    "actual":    actual,
                    "consenso":  consenso,
                    "anterior":  e.get("anterior"),
                    "descricao": f"{e['evento']}: real {actual} vs consenso {consenso}",
                })

    return eventos


def ha_gatilho(precos: dict) -> bool:
    return len(detectar_eventos(precos)) > 0
