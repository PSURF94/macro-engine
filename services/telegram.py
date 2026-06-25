import io
import os
import re
import requests
from datetime import datetime
from fpdf import FPDF
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

EMOJI_MAP = {
    "🟢": "[RISK-ON]",  "🔴": "[RISK-OFF]", "🟡": "[TRANSICAO]",
    "🌍": "",            "💧": "",            "🎯": "",
    "📊": "",            "📅": "",            "🧠": "",
    "🏆": "",            "💰": "",            "⚠️": "[ATENCAO]",
    "🚨": "[ALERTA]",   "⚡": "Intraday:",   "📈": "Swing:",
    "🥇": "1.",          "🥈": "2.",          "🥉": "3.",
    "4️⃣ ": "4.",        "5️⃣ ": "5.",        "✅": "[OK]",
    "❌": "[X]",         "🔺": "[ALTA]",      "🔻": "[QUEDA]",
    "⭐": "*",
}

# caracteres Unicode que viram hífen comum
UNICODE_HIFENS = "‐‑‒–—―−─━﹘﹣－"

SEP_PATTERN = re.compile(r"^[\-—–━─=_*\s]{4,}$")


def _normalizar(texto: str) -> str:
    for ch, sub in EMOJI_MAP.items():
        texto = texto.replace(ch, sub)
    for ch in UNICODE_HIFENS:
        texto = texto.replace(ch, "-")
    texto = texto.replace("’", "'").replace("‘", "'")
    texto = texto.replace("“", '"').replace("”", '"')
    return texto


def _limpar_para_pdf(texto: str) -> str:
    texto = _normalizar(texto)
    linhas = []
    for linha in texto.split("\n"):
        s = linha.strip()
        if s and SEP_PATTERN.match(s):
            linhas.append("---SEP---")
            continue
        s = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", s)
        s = re.sub(r"_{1,2}(.*?)_{1,2}", r"\1", s)
        s = re.sub(r"`[^`\n]+`", "", s)
        s = re.sub(r"^#{1,6}\s+", "", s)
        linhas.append(s)
    texto = "\n".join(linhas)
    texto = re.sub(r"```.*?```", "", texto, flags=re.DOTALL)
    return texto


def _para_latin1(texto: str) -> str:
    return texto.encode("latin-1", errors="ignore").decode("latin-1")


def enviar(texto: str) -> bool:
    MAX = 4096
    partes = [texto[i:i+MAX] for i in range(0, len(texto), MAX)]
    ok = True
    for parte in partes:
        r = requests.post(
            f"{BASE}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": parte},
            timeout=10,
        )
        if not r.ok:
            ok = False
    return ok


def _gerar_pdf(texto: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    limpo = _limpar_para_pdf(texto)

    for linha in limpo.split("\n"):
        l = _para_latin1(linha.rstrip())
        if l.strip() == "---SEP---":
            pdf.ln(2)
            pdf.set_draw_color(150, 150, 150)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + 170, pdf.get_y())
            pdf.ln(3)
            pdf.set_x(pdf.l_margin)
        elif l.strip() == "":
            pdf.ln(2)
        elif l.upper().startswith("MACRO ENGINE"):
            pdf.set_font("Helvetica", style="B", size=13)
            pdf.multi_cell(190, 7, l)
            pdf.set_x(pdf.l_margin)
        else:
            pdf.set_font("Helvetica", size=10)
            pdf.multi_cell(190, 5, l)
            pdf.set_x(pdf.l_margin)

    return bytes(pdf.output())


def enviar_pdf(texto: str, data: str = None) -> bool:
    if data is None:
        data = datetime.now().strftime("%Y-%m-%d")
    filename = f"macro-engine-{data}.pdf"
    pdf_bytes = _gerar_pdf(texto)
    caption = f"Macro Engine | {data}"

    r = requests.post(
        f"{BASE}/sendDocument",
        data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption},
        files={"document": (filename, io.BytesIO(pdf_bytes), "application/pdf")},
        timeout=20,
    )
    if not r.ok:
        enviar(f"[PDF falhou] {r.text[:200]}\n\n{texto[:2000]}")
    return r.ok
