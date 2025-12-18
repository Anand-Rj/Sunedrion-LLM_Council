from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from backend.council_manager_sse import run_llm_council_sse

router = APIRouter()

@router.get("/council-sse")
async def sse_stream(request: Request, prompt: str):
    async def event_generator():
        async for event in run_llm_council_sse(prompt):
            # If client disconnects → stop immediately
            if await request.is_disconnected():
                break
            yield f"data: {event}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
