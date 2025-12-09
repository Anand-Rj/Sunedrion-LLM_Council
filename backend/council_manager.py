import asyncio
from prompt_optimizer import optimize_prompt_for_all
from model_clients.gemini_client import call_gemini
from model_clients.claude_client import call_claude
from model_clients.perplexity_client import call_perplexity
from model_clients.grok_client import call_grok
from model_clients.you_client import call_you
from model_clients.kimi_client import call_kimi
from model_clients.deepseek_client import call_deepseek
from model_clients.openai_client import call_openai_style
from config import Config
from debate_engine import chairman_arbitrate
from memory_engine import MemoryEngine

memory = MemoryEngine()

async def run_llm_council(user_prompt: str):
    improved_prompt = memory.adjust_prompt(user_prompt)
    prompts = optimize_prompt_for_all(improved_prompt)

    tasks = [
        call_openai_style(prompts["openai"], Config.OPENAI_BASE, Config.OPENAI_MODEL, Config.OPENAI_API_KEY),
        call_claude(prompts["claude"]),
        call_perplexity(prompts["perplexity"]),
        call_grok(prompts["grok"]),
        call_kimi(prompts["kimi"]),
        call_you(prompts["ari"]),
        call_deepseek(prompts["deepseek"])
    ]

    results = await asyncio.gather(*tasks)

    outputs = {
        "openai": results[0],
        "claude": results[1],
        "perplexity": results[2],
        "grok": results[3],
        "kimi": results[4],
        "ari": results[5],
        "deepseek": results[6]
    }

    final_answer, scores = await chairman_arbitrate(user_prompt, outputs)

    memory.store_record(user_prompt, outputs, scores)

    return {"final": final_answer, "scores": scores, "outputs": outputs}

