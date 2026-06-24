from http.server import BaseHTTPRequestHandler
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.finnhub_client import coletar_precos, calendario_hoje
from services.rss_client import headlines_recentes
from services.gemini_client import gerar_analise
from services.telegram import enviar
from modules.eventos import detectar_eventos

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

            dados = {
                "eventos": eventos,
                "precos": precos,
                "calendario": calendario_hoje(),
                "headlines": headlines_recentes(janela_horas=1)[:5],
                "instrucao": "Para cada evento detectado, aplique o MOTOR DE EVENTOS do PROMPT-SISTEMA com análise das 3 perguntas.",
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
