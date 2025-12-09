import aiohttp
from backend.config import Config

async def call_claude(prompt: str):
    headers = {
        "x-api-key": Config.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }

    payload = {
        "model": Config.CLAUDE_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4096
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(Config.ANTHROPIC_BASE, headers=headers, json=payload) as resp:
            data = await resp.json()
            try:
                return data["content"][0]["text"]
            except:
                return f"[Claude Error] {data}"

