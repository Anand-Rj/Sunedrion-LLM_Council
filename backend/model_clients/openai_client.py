import aiohttp
from backend.config import Config

async def call_openai(prompt: str):
    headers = {
        "Authorization": f"Bearer {Config.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": Config.OPENAI_MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(Config.OPENAI_BASE, headers=headers, json=payload) as resp:
            try:
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
            except:
                return f"[OpenAI Error] {await resp.text()}"
