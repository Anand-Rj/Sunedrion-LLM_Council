import os

def clean(x):
    return x.strip() if x else None

class Config:
    # BASE URLs
    OPENAI_BASE = "https://api.openai.com/v1/chat/completions"
    ANTHROPIC_BASE = "https://api.anthropic.com/v1/messages"
    PERPLEXITY_BASE = "https://api.perplexity.ai/chat/completions"
    DEEPSEEK_BASE = "https://api.deepseek.com/v1/chat/completions"
    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

    # MODELS
    OPENAI_MODEL = "gpt-5.1"
    CLAUDE_MODEL = "claude-opus-4-5-20251101"
    PERPLEXITY_MODEL = "sonar-pro"
    DEEPSEEK_MODEL = "deepseek-chat"
    KIMI_MODEL = "moonshotai/kimi-k2-thinking"  # via OpenRouter

    # CHAIRMAN (Gemini)
    CHAIRMAN_MODEL = "google/gemini-3-pro-preview"

    # KEYS
    OPENAI_API_KEY = clean(os.getenv("OPENAI_API_KEY"))
    ANTHROPIC_API_KEY = clean(os.getenv("ANTHROPIC_API_KEY"))
    PERPLEXITY_API_KEY = clean(os.getenv("PERPLEXITY_API_KEY"))
    DEEPSEEK_API_KEY = clean(os.getenv("DEEPSEEK_API_KEY"))
    OPENROUTER_API_KEY = clean(os.getenv("OPENROUTER_API_KEY"))
