# backend/council_manager_sse.py

import asyncio
import json

from backend.prompt_optimizer import optimize_prompt_for_all
from backend.model_clients.openai_client import call_openai_style
from backend.model_clients.claude_client import call_claude
from backend.model_clients.perplexity_client import call_perplexity
from backend.model_clients.kimi_client import call_kimi
from backend.model_clients.deepseek_client import call_deepseek
from backend.timeout_wrapper import run_with_timeout
from backend.config import Config
from backend.debate_engine import chairman_arbitrate
from backend.memory_engine import MemoryEngine

memory = MemoryEngine()


# ============================================================
#  SSE Streaming Council Manager
# ============================================================

async def run_llm_council_sse(user_prompt: str):
    """
    Streaming version of the LLM council:
    - Sends each model's result as soon as it's ready
    - Sends final answer
    - Sends JSON-safe scores
    """

    # STEP 1 — Improve prompt & optimize per model
    improved_prompt = memory.adjust_prompt(user_prompt)
    prompts = optimize_prompt_for_all(improved_prompt)

    TIMEOUT_OPENAI = 45
    TIMEOUT_CLAUDE = 30
    TIMEOUT_PERPLEXITY = 25
    TIMEOUT_KIMI = 65
    TIMEOUT_DEEPSEEK = 50

    # STEP 2 — Prepare async coroutine list
    coroutines = [
        ("openai", run_with_timeout(
            call_openai_style(
                prompts["openai"],
                Config.OPENAI_BASE,
                Config.OPENAI_MODEL,
                Config.OPENAI_API_KEY
            ),
            TIMEOUT_OPENAI
        )),
        ("claude", run_with_timeout(call_claude(prompts["claude"]), TIMEOUT_CLAUDE)),
        ("perplexity", run_with_timeout(call_perplexity(prompts["perplexity"]), TIMEOUT_PERPLEXITY)),
        ("kimi", run_with_timeout(call_kimi(prompts["kimi"]), TIMEOUT_KIMI)),
        ("deepseek", run_with_timeout(call_deepseek(prompts["deepseek"]), TIMEOUT_DEEPSEEK)),
    ]

    # Map model -> output
    outputs = {}

    # STEP 3 — Stream results as each model finishes
    tasks = {asyncio.create_task(coro): model for model, coro in coroutines}

    for task in asyncio.as_completed(tasks):
        model = tasks[task]

        try:
            result = await task
        except Exception as e:
            result = f"ERROR: {str(e)}"

        outputs[model] = result

        # Stream model output
        safe_output = str(result).replace("\n", "\\n")
        yield f"event: model_output\ndata: {model}|{safe_output}\n\n"

    # STEP 4 — Pass results to chairman
    final_answer, scores = await chairman_arbitrate(user_prompt, outputs)

    # Save memory record
    memory.store_record(user_prompt, outputs, scores)

    # STEP 5 — Send final answer
    safe_final = final_answer.replace("\n", "\\n")
    yield f"event: final_answer\ndata: {safe_final}\n\n"

    # STEP 6 — Stream proper JSON scores
    json_scores = json.dumps(scores)  # ⭐ FIX: Valid JSON with double quotes
    yield f"event: scores\ndata: {json_scores}\n\n"

    # STEP 7 — Done event
    yield "event: done\ndata: done\n\n"
