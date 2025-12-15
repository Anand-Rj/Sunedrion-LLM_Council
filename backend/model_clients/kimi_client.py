import aiohttp
import asyncio
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

    try:
        # 🔥 KIMI needs a higher timeout
        async with asyncio.timeout(65):   # 65s total for KIMI
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    Config.KIMI_OPENROUTER_URL,
                    json=payload,
                    headers=headers,
                    ssl=False    # fixes random TLS/stream resets
                ) as resp:

                    # Try JSON first
                    try:
                        return await resp.json()
                    except:
                        return await resp.text()

    except TimeoutError:
        return "TIMEOUT"

    except Exception as e:
        return f"KIMI ERROR: {str(e)}"
