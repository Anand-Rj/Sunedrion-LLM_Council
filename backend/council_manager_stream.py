# backend/council_manager_stream.py

import asyncio
from backend.prompt_optimizer import optimize_prompt_for_all
from backend.model_clients.openai_client import call_openai_style
from backend.model_clients.claude_client import call_claude
from backend.model_clients.perplexity_client import call_perplexity
from backend.model_clients.kimi_client import call_kimi
from backend.model_clients.deepseek_client import call_deepseek
from backend.debate_engine import chairman_arbitrate
from backend.memory_engine import MemoryEngine
from backend.timeout_wrapper import run_with_timeout
from backend.config import Config

memory = MemoryEngine()

async def run_llm_council_stream(prompt: str):
    improved = memory.adjust_prompt(prompt)
    prompts = optimize_prompt_for_all(improved)

    # Notify frontend
    yield "STATUS:START"

    # TIMEOUTS
    TIMEOUT = {
        "openai": 45,
        "claude": 30,
        "perplexity": 25,
        "kimi": 60,
        "deepseek": 55
    }

    async def run_delegate(name, coro):
        yield f"{name.upper()}:STARTED"
        result = await run_with_timeout(coro, TIMEOUT[name])
        yield f"{name.upper()}:FINISHED:{result}"
        return result

    # Run delegate models concurrently
    tasks = {
        "openai": run_delegate("openai", call_openai_style(prompts["openai"], Config.OPENAI_BASE, Config.OPENAI_MODEL, Config.OPENAI_API_KEY)),
        "claude": run_delegate("claude", call_claude(prompts["claude"])),
        "perplexity": run_delegate("perplexity", call_perplexity(prompts["perplexity"])),
        "kimi": run_delegate("kimi", call_kimi(prompts["kimi"])),
        "deepseek": run_delegate("deepseek", call_deepseek(prompts["deepseek"]))
    }

    # Stream results as they complete
    results = {}
    for name, coro in tasks.items():
        async for update in coro:
            yield update
        results[name] = update.split(":", 2)[2]  # extract final result

    # Chairman step
    yield "CHAIRMAN:STARTED"
    final_answer, scores = await chairman_arbitrate(prompt, results)
    yield f"CHAIRMAN:FINAL:{final_answer}"
    yield f"CHAIRMAN:SCORES:{scores}"

    # Store memory
    memory.store_record(prompt, results, scores)

    yield "STATUS:COMPLETE"
