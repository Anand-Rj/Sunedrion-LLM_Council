from model_clients.openai_client import call_openai_style
from config import Config

async def call_perplexity(prompt: str):
    return await call_openai_style(
        prompt, Config.PERPLEXITY_BASE, Config.PERPLEXITY_MODEL, Config.PERPLEXITY_API_KEY
    )

