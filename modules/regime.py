def calcular_score_liquidez(macro: dict, precos: dict) -> int:
    score = 0

    t10 = macro.get("treasury_10y", {}).get("atual", 0)
    t10_ant = macro.get("treasury_10y", {}).get("anterior", t10)
    fed = macro.get("fed_funds", {}).get("atual", 0)
    juros_reais = t10 - 2.5  # proxy inflação esperada
    if juros_reais < 0 or t10 < t10_ant:
        score += 1

    dxy = precos.get("dxy", {})
    if dxy and dxy.get("var_dia_pct", 0) < -0.2:
        score += 1

    m2 = macro.get("m2", {})
    if m2 and m2.get("variacao", 0) >= 0:
        score += 1

    sp = precos.get("sp500", {})
    nq = precos.get("nasdaq", {})
    if sp and nq:
        if sp.get("var_dia_pct", 0) > 0 and nq.get("var_dia_pct", 0) > 0:
            score += 1

    # VIXY (proxy VIX): queda no dia = volatilidade cedendo = sinal risk-on
    vix = precos.get("vix", {})
    if vix and vix.get("var_dia_pct", 0) < -2:
        score += 1

    return score


def classificar_regime(score_liquidez: int, precos: dict, macro: dict) -> dict:
    sp_var = precos.get("sp500", {}).get("var_dia_pct", 0) or 0
    btc_var = precos.get("btc", {}).get("var_dia_pct", 0) or 0
    dxy_var = precos.get("dxy", {}).get("var_dia_pct", 0) or 0

    if score_liquidez >= 4:
        regime = "Risk-On"
        emoji = "🟢"
    elif score_liquidez <= 2:
        regime = "Risk-Off"
        emoji = "🔴"
    else:
        regime = "Transição"
        emoji = "🟡"

    # confiança: coerência entre ativos
    sinais = []
    if regime == "Risk-On":
        sinais = [sp_var > 0, btc_var > 0, dxy_var < 0]
    elif regime == "Risk-Off":
        sinais = [sp_var < 0, btc_var < 0, dxy_var > 0]
    else:
        sinais = [abs(sp_var) < 0.5, abs(btc_var) < 1]

    coerencia = sum(sinais) / len(sinais) if sinais else 0.5
    confianca_base = 40 + int(coerencia * 50) + (score_liquidez * 2)
    confianca = min(confianca_base, 98)

    return {
        "regime": regime,
        "emoji": emoji,
        "score_liquidez": score_liquidez,
        "confianca_pct": confianca,
    }


def calcular_prob_mudanca(regime: str, confianca: int, n_eventos_criticos: int) -> dict:
    base_continuar = confianca
    penalidade_eventos = min(n_eventos_criticos * 10, 30)
    continuar = max(base_continuar - penalidade_eventos, 10)
    transicao = max(100 - continuar - 10, 5)
    virada = max(100 - continuar - transicao, 5)

    # normalizar para somar 100
    total = continuar + transicao + virada
    return {
        "continuar": round(continuar / total * 100),
        "transicao": round(transicao / total * 100),
        "virada": round(virada / total * 100),
    }
