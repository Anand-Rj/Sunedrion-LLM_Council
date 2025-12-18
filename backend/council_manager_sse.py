import asyncio
import json

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


# ---------------------------------------------------------
#  MODEL RUNNER (async generator)
# ---------------------------------------------------------
async def run_model(model_name, coro):
    """Runs a model coroutine and streams intermediate updates."""

    # Notify frontend the model has started
    yield f"event:model_start\ndata:{model_name}\n\n"

    try:
        result = await coro
        yield f"event:model_output\ndata:{json.dumps({'model': model_name, 'output': result})}\n\n"

    except Exception as e:
        yield f"event:model_error\ndata:{json.dumps({'model': model_name, 'error': str(e)})}\n\n"

    # Optional clean finish event
    yield f"event:model_done\ndata:{model_name}\n\n"


# ---------------------------------------------------------
#  MAIN SSE COUNCIL PIPELINE
# ---------------------------------------------------------
async def run_llm_council_sse(user_prompt: str):
    """Master SSE generator producing a continuous server-sent stream."""

    # 1️⃣ Memory-enhanced & optimized prompt
    improved = memory.adjust_prompt(user_prompt)
    prompts = optimize_prompt_for_all(improved)

    yield f"event:log\ndata:Prompt optimized\n\n"

    # 2️⃣ Prepare model tasks
    tasks = {
        "openai": run_with_timeout(
            call_openai_style(
                prompts["openai"],
                Config.OPENAI_BASE,
                Config.OPENAI_MODEL,
                Config.OPENAI_API_KEY
            ), 45
        ),
        "claude": run_with_timeout(call_claude(prompts["claude"]), 30),
        "perplexity": run_with_timeout(call_perplexity(prompts["perplexity"]), 25),
        "kimi": run_with_timeout(call_kimi(prompts["kimi"]), 60),
        "deepseek": run_with_timeout(call_deepseek(prompts["deepseek"]), 50),
    }

    # 3️⃣ Stream each model concurrently
    model_outputs = {}

    async def run_and_collect(name, task):
        async for event in run_model(name, task):
            yield event
        model_outputs[name] = await task

    # Run all in parallel
    coros = [run_and_collect(name, task) for name, task in tasks.items()]

    for combined in asyncio.as_completed(coros):
        async for msg in await combined:
            yield msg

    yield f"event:log\ndata:All models finished\n\n"

    # 4️⃣ Send outputs to chairman arbitration
    yield f"event:log\ndata:Running chairman arbitration...\n\n"

    final_answer, scores = await chairman_arbitrate(user_prompt, model_outputs)

    # 5️⃣ Stream final results
    yield f"event:final_answer\ndata:{json.dumps(final_answer)}\n\n"
    yield f"event:scores\ndata:{json.dumps(scores)}\n\n"

    # 6️⃣ Store memory
    memory.store_record(user_prompt, model_outputs, scores)

    yield f"event:done\ndata:complete\n\n"
