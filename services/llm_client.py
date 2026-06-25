import httpx
import json
from config import CEREBRAS_API_KEY, CEREBRAS_MODEL


def gerar_analise(system_prompt: str, dados: dict) -> str:
    payload = {
        "model": CEREBRAS_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Dados para análise:\n\n```json\n{json.dumps(dados, ensure_ascii=False, indent=2)}\n```",
            },
        ],
        "temperature": 0.3,
        "max_tokens": 2048,
    }

    with httpx.Client(timeout=30) as client:
        r = client.post(
            "https://api.cerebras.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {CEREBRAS_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
