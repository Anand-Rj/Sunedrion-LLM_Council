from fastapi import APIRouter
from backend.council_manager import run_council

router = APIRouter(prefix="/council", tags=["Council"])

@router.post("/run")
async def run(prompt: str):
    return await run_council(prompt)
