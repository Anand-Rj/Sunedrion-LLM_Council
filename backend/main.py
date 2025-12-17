from fastapi import FastAPI
from backend.websocket_endpoint import router as ws_router

app = FastAPI()

# Add WebSocket router
app.include_router(ws_router)
