import yfinance as yf
from config import ATIVOS_YFINANCE


def coletar_precos() -> dict:
    resultado = {}
    for nome, ticker in ATIVOS_YFINANCE.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="5d", interval="1h")
            if hist.empty:
                resultado[nome] = None
                continue
            ultimo = hist["Close"].iloc[-1]
            anterior_1h = hist["Close"].iloc[-2] if len(hist) > 1 else ultimo
            abertura_dia = hist["Close"].iloc[-8] if len(hist) >= 8 else hist["Close"].iloc[0]
            resultado[nome] = {
                "ticker": ticker,
                "preco": round(float(ultimo), 4),
                "var_1h_pct": round((ultimo - anterior_1h) / anterior_1h * 100, 3),
                "var_dia_pct": round((ultimo - abertura_dia) / abertura_dia * 100, 3),
            }
        except Exception as e:
            resultado[nome] = {"erro": str(e)}
    return resultado
