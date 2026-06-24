import httpx
import json
from config import GEMINI_API_KEY, GEMINI_MODEL

BASE = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def gerar_analise(system_prompt: str, dados: dict) -> str:
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"Dados para análise:\n\n```json\n{json.dumps(dados, ensure_ascii=False, indent=2)}\n```"}],
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 2048,
        },
    }

    with httpx.Client(timeout=25) as client:
        r = client.post(
            BASE,
            headers={"x-goog-api-key": GEMINI_API_KEY, "Content-Type": "application/json"},
            json=payload,
        )
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
