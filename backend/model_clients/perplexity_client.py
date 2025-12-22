from backend.config import Config
import aiohttp

async def call_perplexity(prompt: str):
    headers = {
        "Authorization": f"Bearer {Config.PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": Config.PERPLEXITY_MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(Config.PERPLEXITY_BASE, headers=headers, json=payload) as resp:
            try:
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
            except:
                return f"[Perplexity Error] {await resp.text()}"
