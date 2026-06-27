from http.server import BaseHTTPRequestHandler
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.finnhub_client import coletar_precos
from services.fred_client import coletar_macro
from services.coingecko_client import coletar_cripto
from services.rss_client import headlines_recentes
from services.llm_client import gerar_analise
from services.telegram import enviar
from modules.regime import calcular_score_liquidez, classificar_regime
from modules.eventos import detectar_eventos
from datetime import datetime, timezone, timedelta

BRT = timezone(timedelta(hours=-3))

with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "PROMPT-SISTEMA.md")) as f:
    SYSTEM_PROMPT = f.read()


def gerar_monitor() -> str | None:
    agora = datetime.now(tz=BRT)
    if agora.weekday() >= 5:  # 5=sábado, 6=domingo
        return None

    hora_atual = agora.strftime("%H:%M")

    precos = coletar_precos()
    macro  = coletar_macro()
    cripto = coletar_cripto()
    news   = headlines_recentes(janela_horas=1)
    eventos = detectar_eventos(precos)

    score_liq   = calcular_score_liquidez(macro, precos)
    regime_data = classificar_regime(score_liq, precos, macro)

    # somente envia se houver algo relevante
    tem_alerta = (
        regime_data["confianca_pct"] < 65
        or len(eventos) > 0
        or regime_data["regime"] == "Transição"
    )
    if not tem_alerta:
        return None

    dados = {
        "hora_atual": hora_atual,
        "regime": regime_data,
        "precos": precos,
        "macro": macro,
        "cripto": cripto,
        "eventos_detectados": eventos,
        "headlines": news[:5],
        "instrucao": f"Gere o MONITOR HORÁRIO no formato compacto do PROMPT-SISTEMA. O horário atual em BRT é {hora_atual} — use exatamente esse valor em 'MONITOR [HH:MM]'.",
    }

    return gerar_analise(SYSTEM_PROMPT, dados)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            msg = gerar_monitor()
            if msg:
                enviar(msg)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
