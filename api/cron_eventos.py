from http.server import BaseHTTPRequestHandler
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.finnhub_client import coletar_precos, calendario_hoje
from services.fred_client import coletar_macro
from services.coingecko_client import coletar_cripto
from services.rss_client import headlines_recentes
from services.llm_client import gerar_analise
from services.telegram import enviar
from modules.eventos import detectar_eventos
from modules.regime import calcular_score_liquidez, classificar_regime
from modules.ranking import gerar_ranking

with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "PROMPT-SISTEMA.md")) as f:
    SYSTEM_PROMPT = f.read()


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            precos  = coletar_precos()
            eventos = detectar_eventos(precos)

            if not eventos:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"NO_EVENTS")
                return

            macro       = coletar_macro()
            cripto      = coletar_cripto()
            score_liq   = calcular_score_liquidez(macro, precos)
            regime_data = classificar_regime(score_liq, precos, macro)
            ranking     = gerar_ranking(regime_data["regime"], precos, cripto)

            dados = {
                "eventos":  eventos,
                "precos":   precos,
                "regime":   regime_data,
                "ranking":  ranking,
                "calendario": calendario_hoje(),
                "headlines": headlines_recentes(janela_horas=1)[:5],
                "instrucao": (
                    "Aplique o MOTOR DE EVENTOS do PROMPT-SISTEMA para cada evento detectado. "
                    "Ao final, inclua a secao VALE OLHAR listando apenas os ativos com vale_olhar=true no ranking. "
                    "Se nenhum ativo tiver vale_olhar=true, escreva 'VALE OLHAR: nenhum — aguardar melhor contexto'."
                ),
            }

            analise = gerar_analise(SYSTEM_PROMPT, dados)
            enviar(analise)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
