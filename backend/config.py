import os
from dotenv import load_dotenv

load_dotenv()

class Config:

    # -----------------------------
    # BASE URLs (UNCHANGED)
    # -----------------------------
    OPENAI_BASE = "https://api.openai.com/v1/chat/completions"
    PERPLEXITY_BASE = "https://api.perplexity.ai/chat/completions"
    GROK_BASE = "https://api.x.ai/v1/chat/completions"
    #KIMI_BASE = "https://kimi-k2.ai/api/v1/chat/completions"
    YOU_BASE = "https://api.you.com/v1/chat/completions"
    DEEPSEEK_BASE = "https://api.deepseek.com/v1/chat/completions"
    ANTHROPIC_BASE = "https://api.anthropic.com/v1/messages"

    # -----------------------------
    # MODELS (UNCHANGED)
    # -----------------------------
    OPENAI_MODEL = "gpt-5.1"
    CLAUDE_MODEL = "claude-opus-4-5-20251101"
    PERPLEXITY_MODEL = "sonar-pro"
    GROK_MODEL = "grok-2-latest"
    #KIMI_MODEL = "kimi-k2-thinking"
    YOU_MODEL = "gpt-4.1"
    DEEPSEEK_MODEL = "deepseek-chat"

    # -----------------------------
    # API KEYS (UNCHANGED)
    # -----------------------------
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
    GROK_API_KEY = os.getenv("GROK_API_KEY")
    #KIMI_API_KEY = os.getenv("KIMI_API_KEY")
    YOU_API_KEY = os.getenv("YOU_API_KEY")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    # ======================================================
    # 🚀 GEMINI (ONLY VIA OPENROUTER)
    # ======================================================
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

    GEMINI_OPENROUTER_MODEL = "google/gemini-3-pro-preview"
    GEMINI_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

    # Chairman model
    CHAIRMAN_MODEL = GEMINI_OPENROUTER_MODEL


    # KIMI via OPENROUTER
    KIMI_OPENROUTER_MODEL = "moonshotai/kimi-k2-thinking"
    KIMI_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"