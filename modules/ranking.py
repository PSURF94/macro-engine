def pontuar_ativo(nome: str, regime: str, preco_data: dict, cripto_data: dict = None) -> float:
    if not preco_data or "erro" in preco_data:
        return 0.0

    var_dia = preco_data.get("var_dia_pct", 0) or 0
    var_1h  = preco_data.get("var_1h_pct", 0) or 0
    nota = 0.0

    # alinhamento com regime (0–3)
    if regime == "Risk-On":
        alinhado = nome in ("sp500", "nasdaq", "btc", "ouro")
        if alinhado and var_dia > 0:
            nota += 3
        elif alinhado:
            nota += 1.5
    elif regime == "Risk-Off":
        alinhado = nome in ("dxy", "ouro")
        if alinhado and var_dia > 0:
            nota += 3
        elif alinhado:
            nota += 1.5
    else:
        nota += 1.0  # transição: todos recebem ponto neutro

    # força da tendência (0–3)
    forca = min(abs(var_dia) / 2, 3)
    if var_dia > 0:
        nota += forca
    elif var_dia < 0 and regime == "Risk-Off" and nome in ("dxy", "ouro"):
        nota += forca

    # momentum 1h (0–2)
    if var_1h > 0 and var_dia > 0:
        nota += min(abs(var_1h) / 0.5, 2)

    # dominância BTC (0–2) — bônus cripto quando dominância alta
    if nome == "btc" and cripto_data:
        dom = cripto_data.get("btc_dominancia_pct", 50)
        if dom > 55:
            nota += 1.5
        elif dom > 50:
            nota += 1.0

    return round(min(nota, 10.0), 1)


MEDALHAS = ["🥇", "🥈", "🥉", "4️⃣ ", "5️⃣ "]
NOMES_PT = {
    "sp500": "S&P 500",
    "nasdaq": "Nasdaq",
    "btc": "Bitcoin",
    "ouro": "Ouro",
    "dxy": "USD (DXY)",
}


def gerar_ranking(regime: str, precos: dict, cripto: dict) -> list[dict]:
    scores = {}
    for nome in ("sp500", "nasdaq", "btc", "ouro", "dxy"):
        scores[nome] = pontuar_ativo(nome, regime, precos.get(nome, {}), cripto)

    ordenado = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [
        {
            "medalha": MEDALHAS[i],
            "ativo": NOMES_PT[nome],
            "nota": nota,
        }
        for i, (nome, nota) in enumerate(ordenado)
    ]


def formatar_ranking(ranking: list[dict]) -> str:
    linhas = []
    for item in ranking:
        linhas.append(f"{item['medalha']} {item['ativo']} — {item['nota']}/10")
    return "\n".join(linhas)
