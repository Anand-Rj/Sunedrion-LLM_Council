from backend.model_clients.openai_client import call_openai_style
from backend.config import Config

async def call_deepseek(prompt: str):
    return await call_openai_style(
        prompt, Config.DEEPSEEK_BASE, Config.DEEPSEEK_MODEL, Config.DEEPSEEK_API_KEY
    )

