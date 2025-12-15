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

        totals = {"openai":0,"claude":0,"perplexity":0,"kimi":0,"deepseek":0}

        for rec in data["history"]:
            for model, score in rec["scores"].items():
                totals[model] += score

        best = max(totals, key=totals.get)

        return f"[This task benefits from {best}] {user_prompt}"

