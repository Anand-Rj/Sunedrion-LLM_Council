from fastapi import FastAPI
from pydantic import BaseModel
from backend.council_manager import run_llm_council


app = FastAPI()

class UserPrompt(BaseModel):
    prompt: str

@app.post("/council")
async def council_api(data: UserPrompt):
    return await run_llm_council(data.prompt)
