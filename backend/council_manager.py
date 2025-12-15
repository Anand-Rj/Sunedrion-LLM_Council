import asyncio
from backend.prompt_optimizer import optimize_prompt_for_all
from backend.model_clients.gemini_client import call_gemini
from backend.model_clients.claude_client import call_claude
from backend.model_clients.perplexity_client import call_perplexity
from backend.model_clients.kimi_client import call_kimi
from backend.model_clients.deepseek_client import call_deepseek
from backend.model_clients.openai_client import call_openai_style
from backend.timeout_wrapper import run_with_timeout
from backend.config import Config
from backend.debate_engine import chairman_arbitrate
from backend.memory_engine import MemoryEngine

memory = MemoryEngine()

async def run_llm_council(user_prompt: str):

    improved_prompt = memory.adjust_prompt(user_prompt)
    prompts = optimize_prompt_for_all(improved_prompt)

    # Wrap each call with timeout
    tasks = [
        run_with_timeout(
            call_openai_style(prompts["openai"], Config.OPENAI_BASE, Config.OPENAI_MODEL, Config.OPENAI_API_KEY)
        ),
        run_with_timeout(call_claude(prompts["claude"])),
        run_with_timeout(call_perplexity(prompts["perplexity"])),
        run_with_timeout(call_kimi(prompts["kimi"])),
        run_with_timeout(call_deepseek(prompts["deepseek"])),
    ]

    results = await asyncio.gather(*tasks)

    outputs = {
        "openai": results[0],
        "claude": results[1],
        "perplexity": results[2],
        "kimi": results[3],
        "deepseek": results[4]
    }

    final_answer, scores = await chairman_arbitrate(user_prompt, outputs)

    memory.store_record(user_prompt, outputs, scores)

    return {"final": final_answer, "scores": scores, "outputs": outputs}
