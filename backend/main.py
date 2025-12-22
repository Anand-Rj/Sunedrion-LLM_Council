from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.council import router as council_router

app = FastAPI(title="Sunedrion LLM Council – Stable API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(council_router)

@app.get("/")
def root():
    return {"status": "Sunedrion backend running"}
