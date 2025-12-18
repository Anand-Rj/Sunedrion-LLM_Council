import asyncio
from backend.prompt_optimizer import optimize_prompt_for_all
from backend.model_clients.openai_client import call_openai_style
from backend.model_clients.claude_client import call_claude
from backend.model_clients.perplexity_client import call_perplexity
from backend.model_clients.kimi_client import call_kimi
from backend.model_clients.deepseek_client import call_deepseek
from backend.debate_engine import chairman_arbitrate
from backend.memory_engine import MemoryEngine
from backend.config import Config

memory = MemoryEngine()

async def run_single_model(model_name, coro):
    """
    Wrapper that ensures the model task always returns a tuple:
    ("model_name", result_string)
    """
    try:
        result = await coro
    except Exception as e:
        result = f"ERROR: {str(e)}"

    return model_name, result


async def run_llm_council_sse(prompt: str):
    """Async generator producing SSE messages."""

    improved_prompt = memory.adjust_prompt(prompt)
    prompts = optimize_prompt_for_all(improved_prompt)

    # Build COROUTINE TASKS (not generators)
    tasks = [
        run_single_model("openai",
            call_openai_style(
                prompts["openai"],
                Config.OPENAI_BASE,
                Config.OPENAI_MODEL,
                Config.OPENAI_API_KEY
            )
        ),

        run_single_model("claude", call_claude(prompts["claude"])),
        run_single_model("perplexity", call_perplexity(prompts["perplexity"])),
        run_single_model("kimi", call_kimi(prompts["kimi"])),
        run_single_model("deepseek", call_deepseek(prompts["deepseek"])),
    ]

    # Now create asyncio Tasks
    pending = [asyncio.create_task(t) for t in tasks]

    results = {}

    # Stream partial results as they finish
    for completed in asyncio.as_completed(pending):
        model, output = await completed
        results[model] = output

        # Stream model output to client
        yield f"event: model_output\ndata: {model}|{output}\n\n"

    # After all models finish → chairman arbitration
    final_answer, scores = await chairman_arbitrate(prompt, results)

    yield f"event: final_answer\ndata: {final_answer}\n\n"
    yield f"event: scores\ndata: {scores}\n\n"

    memory.store_record(prompt, results, scores)

    yield "event: done\ndata: finished\n\n"
