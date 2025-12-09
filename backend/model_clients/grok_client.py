from backend.model_clients.openai_client import call_openai_style
from backend.config import Config

async def call_grok(prompt: str):
    return await call_openai_style(
        prompt, Config.GROK_BASE, Config.GROK_MODEL, Config.GROK_API_KEY
    )

