from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from backend.council_manager_sse import run_llm_council_sse

router = APIRouter()

@router.get("/sse")
async def council_stream(request: Request, prompt: str):
    async def event_stream():
        async for message in run_llm_council_sse(prompt):
            yield message
    return StreamingResponse(event_stream(), media_type="text/event-stream")
