from fastapi import FastAPI
from pydantic import BaseModel
from backend.council_manager import run_llm_council
import os

app = FastAPI()

class UserPrompt(BaseModel):
    prompt: str

@app.post("/council")
async def council_api(data: UserPrompt):
    return await run_llm_council(data.prompt)


@app.get("/env-debug")
def env_debug():
    return {"env": {k: "SET" for k in os.environ.keys()}}
