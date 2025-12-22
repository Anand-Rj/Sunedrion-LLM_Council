import asyncio
from backend.model_clients.openai_client import call_openai
from backend.model_clients.claude_client import call_claude
from backend.model_clients.perplexity_client import call_perplexity
from backend.model_clients.deepseek_client import call_deepseek
from backend.model_clients.kimi_client import call_kimi
from backend.config import Config
import aiohttp

async def call_chairman(prompt: str, outputs: dict):
    """
    Arbitration by Gemini (OpenRouter)
    """
    headers = {
        "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    arbitration_prompt = (
        f"You are the chairman of a model council.\n\n"
        f"User prompt:\n{prompt}\n\n"
        f"Model responses:\n"
    )
    for k, v in outputs.items():
        arbitration_prompt += f"\n[{k.upper()}]\n{v}\n"

    arbitration_prompt += "\nPick the best answer and explain why."

    payload = {
        "model": Config.CHAIRMAN_MODEL,
        "messages": [{"role": "user", "content": arbitration_prompt}]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(Config.OPENROUTER_URL, headers=headers, json=payload) as resp:
            try:
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
            except:
                return f"[Chairman Error] {await resp.text()}"


async def run_council(prompt: str):
    """
    Execute all 5 delegates in parallel, then chairman.
    """

    tasks = {
        "openai": asyncio.create_task(call_openai(prompt)),
        "claude": asyncio.create_task(call_claude(prompt)),
        "perplexity": asyncio.create_task(call_perplexity(prompt)),
        "deepseek": asyncio.create_task(call_deepseek(prompt)),
        "kimi": asyncio.create_task(call_kimi(prompt)),
    }

    results = {name: await task for name, task in tasks.items()}

    chairman = await call_chairman(prompt, results)

    return {
        "delegate_outputs": results,
        "final_answer": chairman
    }
