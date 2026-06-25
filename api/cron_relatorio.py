from http.server import BaseHTTPRequestHandler
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.finnhub_client import coletar_precos, calendario_hoje
from services.fred_client import coletar_macro
from services.coingecko_client import coletar_cripto
from services.rss_client import headlines_recentes
from services.gemini_client import gerar_analise
from datetime import date
from services.telegram import enviar_pdf
from modules.regime import calcular_score_liquidez, classificar_regime, calcular_prob_mudanca
from modules.ranking import gerar_ranking, formatar_ranking

with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "PROMPT-SISTEMA.md")) as f:
    SYSTEM_PROMPT = f.read()


def gerar_relatorio() -> str:
    precos  = coletar_precos()
    macro   = coletar_macro()
    cripto  = coletar_cripto()
    cal     = calendario_hoje()
    news    = headlines_recentes(janela_horas=2)

    score_liq = calcular_score_liquidez(macro, precos)
    regime_data = classificar_regime(score_liq, precos, macro)
    n_criticos = sum(1 for e in cal if e.get("importancia", 1) >= 3)
    prob = calcular_prob_mudanca(
        regime_data["regime"],
        regime_data["confianca_pct"],
        n_criticos,
    )
    ranking = gerar_ranking(regime_data["regime"], precos, cripto)

    dados = {
        "regime": regime_data,
        "probabilidade_mudanca_5d": prob,
        "score_liquidez": score_liq,
        "precos": precos,
        "macro": macro,
        "cripto": cripto,
        "calendario": cal,
        "headlines": news[:10],
        "ranking": ranking,
        "instrucao": "Gere o RELATÓRIO DIÁRIO completo seguindo exatamente o formato do PROMPT-SISTEMA.",
    }

    return gerar_analise(SYSTEM_PROMPT, dados)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            relatorio = gerar_relatorio()
            enviar_pdf(relatorio, data=date.today().isoformat())
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
