import json
import re
from backend.config import Config
from backend.model_clients.openai_client import call_openai_style
from backend.model_clients.claude_client import call_claude
from backend.model_clients.perplexity_client import call_perplexity
from backend.model_clients.grok_client import call_grok
from backend.model_clients.kimi_client import call_kimi
from backend.model_clients.you_client import call_you
from backend.model_clients.deepseek_client import call_deepseek
from backend.model_clients.gemini_client import call_gemini


# ============================================================
#  JSON Extraction – Bulletproof for Gemini "stringified JSON"
# ============================================================

def extract_json(raw_text: str):
    """Extract the first valid JSON object inside a messy LLM output."""
    if not raw_text:
        return {}

    # 1️⃣ Find a {...} block anywhere in the text
    match = re.search(r"\{[\s\S]*\}", raw_text)
    if not match:
        return {}

    json_block = match.group(0)

    # 2️⃣ Try direct load
    try:
        return json.loads(json_block)
    except json.JSONDecodeError:
        # 3️⃣ Try fixing escaped quotes
        try:
            fixed = json_block.replace("\\\"", "\"")
            return json.loads(fixed)
        except:
            return {}



# ============================================================
#  Run Debate Stage: All Agents Respond
# ============================================================

async def run_debate_round(user_prompt: str):
    """Send user prompt to all delegate models."""

    results = {}

    # Each model wrapped to prevent crashes
    async def safe_call(tag, fn):
        try:
            return await fn(user_prompt)
        except Exception as e:
            return f"[{tag.upper()} ERROR] {str(e)}"

    results["openai"] = await safe_call("openai", call_openai_style)
    results["claude"] = await safe_call("claude", call_claude)
    results["perplexity"] = await safe_call("perplexity", call_perplexity)
    results["grok"] = await safe_call("grok", call_grok)
    results["kimi"] = await safe_call("kimi", call_kimi)
    results["you"] = await safe_call("you", call_you)
    results["deepseek"] = await safe_call("deepseek", call_deepseek)

    return results



# ============================================================
#  Chairman Arbitration (Gemini via OpenRouter)
# ============================================================

async def chairman_arbitrate(user_prompt: str, delegate_outputs: dict):
    """
    Upgraded Chairman model based on Karpathy Council logic.
    The chairman will:
    - Evaluate each response
    - Provide strengths/weaknesses
    - Rank them (internally)
    - Produce a final synthesized answer
    - Output structured JSON like your UI expects
    """

    # Convert delegate outputs into a cleaner table (Karpathy-style)
    formatted_responses = "\n\n".join(
        [f"Model: {model}\nResponse:\n{resp}" for model, resp in delegate_outputs.items()]
    )

    arbitration_prompt = f"""
You are the CHAIRMAN of an AI Council. Multiple delegate AI models have answered a question.

You must evaluate them EXACTLY like Andre Karpathy's LLM Council system:

==========================================================
USER QUESTION:
{user_prompt}

DELEGATE RESPONSES:
{formatted_responses}
==========================================================

Your tasks:

1. Evaluate each response — describe its strengths and weaknesses.
2. Compare responses — note patterns, consensus, contradictions.
3. Rank all responses from best to worst.
4. Synthesize a final combined answer that represents the collective wisdom.
5. OUTPUT ONLY THE FOLLOWING JSON. NOTHING ELSE.

JSON FORMAT (STRICT):

{{
  "final_answer": "...",        ← your synthesized best answer
  "scores": {{
      "openai": 0.0,
      "claude": 0.0,
      "perplexity": 0.0,
      "grok": 0.0,
      "kimi": 0.0,
      "ari": 0.0,
      "deepseek": 0.0
  }}
}}

SCORING RULE:
- Assign each model a score from 0–100 based on answer quality
- Higher = better
- MUST include all models even if their answer is empty

STRICT RULES:
- DO NOT output text outside JSON
- DO NOT explain your reasoning outside JSON
- DO NOT change field names
"""

    # Call Gemini via your existing wrapper
    raw = await call_gemini(arbitration_prompt)

    print("\n=== RAW GEMINI OUTPUT ===")
    print(raw)
    print("=========================\n")

    try:
        content = raw["choices"][0]["message"]["content"]
    except:
        return "Chairman failed to respond.", {
            "openai": 0, "claude": 0, "perplexity": 0,
            "grok": 0, "kimi": 0, "ari": 0, "deepseek": 0
        }

    print("=== GEMINI CONTENT ONLY ===")
    print(content)
    print("===========================\n")

    # Extract JSON
    data = extract_json(content)

    # Validation
    if (
        not isinstance(data, dict)
        or "final_answer" not in data
        or "scores" not in data
    ):
        print("⚠️ CHAIRMAN DID NOT RETURN VALID JSON\n")
        return "Chairman did not produce a valid answer.", {
            "openai": 0,
            "claude": 0,
            "perplexity": 0,
            "grok": 0,
            "kimi": 0,
            "ari": 0,
            "deepseek": 0
        }

    return data["final_answer"], data["scores"]
