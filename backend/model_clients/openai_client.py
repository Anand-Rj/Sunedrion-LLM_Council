# backend/model_clients/openai_client.py

import aiohttp
from config import Config

async def call_openai_style(prompt: str, base_url: str, model: str, api_key: str):
    """
    Generic OpenAI-style chat-completion caller.
    Used by OpenAI, Perplexity, You.com, DeepSeek, Grok (most of them use OpenAI protocol).
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(base_url, json=payload, headers=headers) as resp:
            text = await resp.text()

            # Return raw text (llm response or error)
            try:
                data = await resp.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", text)
            except:
                return text
