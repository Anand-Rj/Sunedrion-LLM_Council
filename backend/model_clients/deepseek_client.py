from backend.config import Config
import aiohttp

async def call_deepseek(prompt: str):
    headers = {
        "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": Config.DEEPSEEK_MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(Config.DEEPSEEK_BASE, headers=headers, json=payload) as resp:
            try:
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
            except:
                return f"[DeepSeek Error] {await resp.text()}"
