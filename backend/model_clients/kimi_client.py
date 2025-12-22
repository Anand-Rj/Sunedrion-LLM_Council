import aiohttp
from backend.config import Config

async def call_kimi(prompt: str):
    headers = {
        "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": Config.KIMI_MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(Config.OPENROUTER_URL, headers=headers, json=payload) as resp:
            try:
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
            except:
                return f"[Kimi Error] {await resp.text()}"
