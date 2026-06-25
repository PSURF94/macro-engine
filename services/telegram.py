import io
import os
import requests
from datetime import datetime
from fpdf import FPDF
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


def _gerar_pdf(texto: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.add_font("DejaVu", "", FONT_PATH)

    for linha in _limpar(texto).split("\n"):
        if linha.startswith("MACRO ENGINE"):
            pdf.set_font("DejaVu", size=13)
            pdf.multi_cell(0, 7, linha)
            pdf.set_font("DejaVu", size=10)
        elif linha.startswith("━"):
            pdf.ln(2)
            pdf.set_draw_color(150, 150, 150)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
            pdf.ln(3)
        elif linha.strip() == "":
            pdf.ln(3)
        else:
            pdf.set_font("DejaVu", size=10)
            pdf.multi_cell(0, 5, linha)

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
