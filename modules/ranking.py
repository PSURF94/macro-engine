# Ativos operáveis: Nasdaq, Ouro, EUR/USD, BTC
# Ativos de regime (filtro apenas): S&P 500, DXY, VIX

ATIVOS_OPERAVEIS = ("nasdaq", "ouro", "eurusd", "btc")

NOMES_PT = {
    "nasdaq": "Nasdaq (NQ)",
    "ouro":   "Ouro (XAU)",
    "eurusd": "EUR/USD",
    "btc":    "Bitcoin",
}

MEDALHAS = ["1.", "2.", "3.", "4."]


def pontuar_ativo(nome: str, regime: str, preco_data: dict, cripto_data: dict = None) -> float:
    if not preco_data or "erro" in preco_data:
        return 0.0

    var_dia = preco_data.get("var_dia_pct", 0) or 0
    var_1h  = preco_data.get("var_1h_pct", 0) or 0
    nota = 0.0

    # alinhamento com regime (0–3)
    if regime == "Risk-On":
        # nasdaq, btc, ouro sobem | eurusd sobe (USD enfraquece)
        alinhado = nome in ("nasdaq", "btc", "ouro", "eurusd")
        if alinhado and var_dia > 0:
            nota += 3
        elif alinhado:
            nota += 1.5
    elif regime == "Risk-Off":
        # ouro sobe | eurusd cai (USD fortalece)
        if nome == "ouro" and var_dia > 0:
            nota += 3
        elif nome == "ouro":
            nota += 1.5
        elif nome == "eurusd" and var_dia < 0:
            # short EUR é o trade em Risk-Off
            nota += 2.5
        elif nome in ("nasdaq", "btc"):
            nota += 0.5  # desfavorecidos
    else:
        nota += 1.0  # transição: neutro

    # força da tendência intraday (0–3)
    forca = min(abs(var_dia) / 2, 3)
    if regime == "Risk-Off" and nome == "eurusd":
        # em Risk-Off, queda do EUR é sinal de força
        if var_dia < 0:
            nota += forca
    elif var_dia > 0:
        nota += forca

    # momentum 1h (0–2)
    momentum_positivo = var_1h > 0 and var_dia > 0
    momentum_short_eur = nome == "eurusd" and regime == "Risk-Off" and var_1h < 0 and var_dia < 0
    if momentum_positivo or momentum_short_eur:
        nota += min(abs(var_1h) / 0.5, 2)

    # bônus BTC: dominância alta favorece BTC sobre altcoins
    if nome == "btc" and cripto_data:
        dom = cripto_data.get("btc_dominancia_pct", 50)
        if dom > 55:
            nota += 1.5
        elif dom > 50:
            nota += 1.0

    return round(min(nota, 10.0), 1)


def gerar_ranking(regime: str, precos: dict, cripto: dict) -> list[dict]:
    scores = {
        nome: pontuar_ativo(nome, regime, precos.get(nome, {}), cripto)
        for nome in ATIVOS_OPERAVEIS
    }
    ordenado = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [
        {"medalha": MEDALHAS[i], "ativo": NOMES_PT[nome], "nota": nota}
        for i, (nome, nota) in enumerate(ordenado)
    ]


def formatar_ranking(ranking: list[dict]) -> str:
    return "\n".join(f"{r['medalha']} {r['ativo']} — {r['nota']}/10" for r in ranking)
