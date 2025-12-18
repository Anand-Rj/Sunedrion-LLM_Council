from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.sse_endpoint import router as sse_router

app = FastAPI()

# Allow Streamlit URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SSE Router
app.include_router(sse_router)
