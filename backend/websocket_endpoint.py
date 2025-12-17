# backend/websocket_endpoint.py

from fastapi import APIRouter, WebSocket
from backend.council_manager_stream import run_llm_council_stream

router = APIRouter()

@router.websocket("/council-stream")
async def council_stream(websocket: WebSocket):
    await websocket.accept()

    # Wait for prompt
    data = await websocket.receive_text()

    # Run streaming council logic
    async for message in run_llm_council_stream(data):
        await websocket.send_text(message)

    await websocket.close()
