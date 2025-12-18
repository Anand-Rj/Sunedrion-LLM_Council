import asyncio
import json

# ---------------------------------------------------
# MOCK CALLS (Replace these with your actual LLM APIs)
# ---------------------------------------------------

async def call_model(name, prompt, timeout=40):
    await asyncio.sleep(1)  # simulate activity
    if name == "deepseek":
        await asyncio.sleep(45)  # forced timeout
    return f"Sample response from {name}"

# ---------------------------------------------------
# REAL STREAMING LOGIC (SSE)
# ---------------------------------------------------

async def run_llm_council_sse(prompt: str):
    models = ["openai", "claude", "perplexity", "kimi", "deepseek"]

    async def run_agent(model):
        try:
            yield f"🟧 {model.upper()} → running…"

            result = await asyncio.wait_for(
                call_model(model, prompt),
                timeout=40
            )

            yield f"🟦 {model.upper()} → completed"
            return model, result

        except asyncio.TimeoutError:
            yield f"🟥 {model.upper()} → timeout"
            return model, None

    # 1️⃣ Run all models concurrently
    tasks = {m: run_agent(m) async for m in {}}

    results = {}

    coroutines = [run_agent(model) for model in models]

    for coro in asyncio.as_completed(coroutines):
        async for msg in await coro:
            yield msg  # send every UI message immediately

        model, output = await coro
        results[model] = output

    # 2️⃣ Chairman synthesizing…
    yield "🏛️ CHAIRMAN → synthesizing…"

    await asyncio.sleep(1)

    final_answer = {
        "final": "Here is the combined council answer (mock).",
        "sources_used": list(results.keys())
    }

    # 3️⃣ FINAL
    yield f"🏁 FINAL → {json.dumps(final_answer)}"
