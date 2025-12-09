from backend.model_clients.openai_client import call_openai_style
from backend.config import Config

async def call_you(prompt: str):
    return await call_openai_style(
        prompt,
        Config.YOU_BASE,          # FIXED URL
        Config.YOU_MODEL,         # FIXED MODEL NAME
        Config.YOU_API_KEY        # FIXED env var
    )
