# main.py

import logging
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.chat import router as chat_router
from app.services.document_loader import ingest
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Focus Advisor",
    description="Evidence-based focus science chatbot with RAG + guardrails",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(chat_router, prefix="/api/v1")


@app.on_event("startup")
async def startup():
    logger.info("Focus Advisor starting up...")
    try:
        ingest(force=False)
        logger.info("Knowledge base ready.")
    except Exception as e:
        logger.warning(f"Startup ingestion skipped: {e}")


@app.get("/")
async def root():
    return FileResponse(os.path.join(STATIC_DIR, "focus_advisor.html"))


@app.get("/health")
async def health():
    return {"status": "ok", "service": "Focus Advisor RAG Chatbot"}
