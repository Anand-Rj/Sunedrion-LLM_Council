import json
from pathlib import Path

class MemoryEngine:
    def __init__(self):
        self.file = Path("council_memory.json")
        if not self.file.exists():
            self.file.write_text(json.dumps({"history": []}, indent=2))

    def load(self):
        return json.loads(self.file.read_text())

    def save(self, data):
        self.file.write_text(json.dumps(data, indent=2))

    def store_record(self, prompt, outputs, scores):
        data = self.load()
        data["history"].append({"prompt": prompt, "outputs": outputs, "scores": scores})
        self.save(data)

    def adjust_prompt(self, user_prompt: str):
        data = self.load()

        if not data["history"]:
            return user_prompt

        # Models you currently support
        valid_models = {"openai", "claude", "perplexity", "kimi", "deepseek"}

        # Initialize totals safely
        totals = {m: 0 for m in valid_models}

        for rec in data["history"]:
            for model, score in rec["scores"].items():
                if model in totals:          # Only count valid models
                    totals[model] += score
                # else ignore removed models like grok, ari, openrouter

        best = max(totals, key=totals.get)

        return f"[This task benefits from {best}] {user_prompt}"

