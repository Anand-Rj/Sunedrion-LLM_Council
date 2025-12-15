import aiohttp
from backend.config import Config

# Load config values from class
OPENROUTER_API_KEY = Config.OPENROUTER_API_KEY
GEMINI_OPENROUTER_MODEL = Config.GEMINI_OPENROUTER_MODEL
GEMINI_OPENROUTER_URL = Config.GEMINI_OPENROUTER_URL

async def call_gemini(prompt: str):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    }

    payload = {
        "model": GEMINI_OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": "You are the chairman. Always return only JSON."},
            {"role": "user", "content": prompt}
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(GEMINI_OPENROUTER_URL, json=payload, headers=headers, timeout=60) as resp:
            try:
                return await resp.json()
            except:
                text = await resp.text()
                return {"error": text}
