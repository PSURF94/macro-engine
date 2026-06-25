import io
import requests
from datetime import datetime
from fpdf import FPDF
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


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
    pdf.set_font("Helvetica", size=10)

    for linha in texto.split("\n"):
        linha_limpa = linha.encode("latin-1", errors="replace").decode("latin-1")
        if linha.startswith("MACRO ENGINE"):
            pdf.set_font("Helvetica", style="B", size=12)
            pdf.multi_cell(0, 6, linha_limpa)
            pdf.set_font("Helvetica", size=10)
        elif linha.startswith("━"):
            pdf.ln(1)
            pdf.set_draw_color(180, 180, 180)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
            pdf.ln(2)
        elif linha.strip() == "":
            pdf.ln(3)
        else:
            pdf.multi_cell(0, 5, linha_limpa)

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
    return r.ok
