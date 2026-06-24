from fredapi import Fred
from config import FRED_API_KEY, FRED_SERIES


_fred = Fred(api_key=FRED_API_KEY)


def coletar_macro() -> dict:
    resultado = {}
    for nome, series_id in FRED_SERIES.items():
        try:
            serie = _fred.get_series(series_id, limit=2)
            valores = serie.dropna()
            atual = float(valores.iloc[-1])
            anterior = float(valores.iloc[-2]) if len(valores) > 1 else atual
            resultado[nome] = {
                "series_id": series_id,
                "atual": round(atual, 4),
                "anterior": round(anterior, 4),
                "variacao": round(atual - anterior, 4),
            }
        except Exception as e:
            resultado[nome] = {"erro": str(e)}
    return resultado
