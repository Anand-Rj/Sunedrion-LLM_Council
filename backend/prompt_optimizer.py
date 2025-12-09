def optimize_prompt_for_all(user_prompt):
    return {
        "openai": f"Provide structured, clear reasoning:\n{user_prompt}",
        "claude": f"Use deep, extended reasoning. Think step-by-step:\n{user_prompt}",
        "perplexity": f"Use grounded research with citations:\n{user_prompt}",
        "grok": f"Provide creative and divergent reasoning:\n{user_prompt}",
        "kimi": f"Include multilingual/worldwide context as needed:\n{user_prompt}",
        "ari": f"Summarize, refactor, and ground the response clearly:\n{user_prompt}",
        "deepseek": f"Break down the problem with strong technical depth:\n{user_prompt}",
    }

