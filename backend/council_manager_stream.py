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

# ----------------------------
# TIMEOUT SETTINGS
# ----------------------------
TIMEOUT = {
    "openai": 45,
    "claude": 30,
    "perplexity": 25,
    "kimi": 65,
    "deepseek": 50,
}


# ============================================================
# STREAMING / ASYNC GENERATOR VERSION OF LLM COUNCIL
# ============================================================

async def run_llm_council_stream(user_prompt: str):
    """
    Streaming version of the Council:
    - Streams progress for each delegate
    - Prevents Render 90s timeout
    - Extremely stable
    """

    # Initial yield
    yield "STATUS:START"

    improved_prompt = memory.adjust_prompt(user_prompt)
    prompts = optimize_prompt_for_all(improved_prompt)

    # Storage for final outputs
    results = {}

    # ------------------------------------------------------------
    # DELEGATE WRAPPER — async generator that yields progress
    # ------------------------------------------------------------
    async def run_delegate(name, coro):
        yield f"{name.upper()}:STARTED"

        # Run with timeout
        result = await run_with_timeout(coro, TIMEOUT[name])

        # Stream finish event
        yield f"{name.upper()}:FINISHED:{result}"

        # Save output into results (replaces illegal return)
        results[name] = result

    # ------------------------------------------------------------
    # BUILD TASKS
    # ------------------------------------------------------------
    tasks = {
        "openai": run_delegate(
            "openai",
            call_openai_style(
                prompts["openai"],
                Config.OPENAI_BASE,
                Config.OPENAI_MODEL,
                Config.OPENAI_API_KEY
            )
        ),
        "claude": run_delegate("claude", call_claude(prompts["claude"])),
        "perplexity": run_delegate("perplexity", call_perplexity(prompts["perplexity"])),
        "kimi": run_delegate("kimi", call_kimi(prompts["kimi"])),
        "deepseek": run_delegate("deepseek", call_deepseek(prompts["deepseek"])),
    }

    # ------------------------------------------------------------
    # STREAM DELEGATE UPDATES
    # ------------------------------------------------------------
    for name, delegate_gen in tasks.items():
        async for update in delegate_gen:
            yield update

    # ------------------------------------------------------------
    # RUN CHAIRMAN
    # ------------------------------------------------------------
    yield "CHAIRMAN:STARTED"

    final_answer, scores = await chairman_arbitrate(user_prompt, results)

    yield "CHAIRMAN:FINISHED"

    # Memory update
    memory.store_record(user_prompt, results, scores)

    # ------------------------------------------------------------
    # SEND FINAL JSON BACK AS STRING
    # (streamlit will parse it)
    # ------------------------------------------------------------
    import json
    final_payload = json.dumps({
        "final": final_answer,
        "scores": scores,
        "outputs": results
    })

    yield f"FINAL_JSON:{final_payload}"
