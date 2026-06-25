import io
import os
import requests
from datetime import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

FONT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "fonts", "DejaVuSans.ttf")

EMOJI_MAP = {
    "🟢": "[RISK-ON]",   "🔴": "[RISK-OFF]",  "🟡": "[TRANSICAO]",
    "🌍": "",             "💧": "",             "🎯": "",
    "📊": "",             "📅": "",             "🧠": "",
    "🏆": "",             "💰": "",             "⚠️": "[ATENCAO]",
    "🚨": "[ALERTA]",    "⚡": "Intraday:",    "📈": "Swing:",
    "🥇": "1.",           "🥈": "2.",           "🥉": "3.",
    "4️⃣": "4.",          "5️⃣": "5.",          "✅": "[OK]",
    "❌": "[X]",          "🔺": "[ALTA]",       "🔻": "[QUEDA]",
}


def _limpar(texto: str) -> str:
    for emoji, sub in EMOJI_MAP.items():
        texto = texto.replace(emoji, sub)
    return "".join(c if ord(c) < 0x3000 else "?" for c in texto)


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


def _para_latin1(texto: str) -> str:
    return texto.encode("latin-1", errors="replace").decode("latin-1")


def _gerar_pdf(texto: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    limpo = _limpar(texto).replace("━", "-" * 40)

    for linha in limpo.split("\n"):
        l = _para_latin1(linha)
        if l.strip() == "":
            pdf.ln(3)
        elif l.startswith("MACRO ENGINE"):
            pdf.set_font("Helvetica", style="B", size=12)
            pdf.multi_cell(0, 7, l, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        elif l.startswith("-" * 10):
            pdf.set_font("Helvetica", size=8)
            pdf.multi_cell(0, 4, l, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            pdf.set_font("Helvetica", size=10)
            pdf.multi_cell(0, 5, l, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

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
