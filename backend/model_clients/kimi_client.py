import aiohttp
from backend.config import Config

async def call_kimi(prompt: str):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
    }

    payload = {
        "model": Config.KIMI_OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": "You are the KIMI delegate model."},
            {"role": "user", "content": prompt}
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(Config.KIMI_OPENROUTER_URL, json=payload, headers=headers, timeout=20) as resp:
            try:
                return await resp.json()
            except:
                return {"error": await resp.text()}
