# app/api/chat.py

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_service import ask
from app.services.document_loader import ingest
from app.services.vector_store import is_populated

router = APIRouter(prefix="/chat", tags=["Focus Advisor"])


class AskRequest(BaseModel):
    question: str
    chat_history: Optional[list] = []

    class Config:
        json_schema_extra = {
            "example": {
                "question": "Why do I lose focus after lunch?",
                "chat_history": []
            }
        }


class AskResponse(BaseModel):
    answer: str
    sources: list
    blocked: bool
    block_category: Optional[str]
    retrieved_chunks: int
    error: Optional[str]


class IngestRequest(BaseModel):
    force: bool = False


@router.get("/health")
async def health():
    populated = is_populated()
    return {
        "status": "ready" if populated else "not_initialized",
        "vector_store_populated": populated,
        "message": "Knowledge base ready" if populated else "POST /chat/ingest to load documents"
    }


@router.post("/ask", response_model=AskResponse)
async def ask_question(req: AskRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    # Filter out any blocked exchanges before sending history to LLM
    clean_history = [
        msg for msg in req.chat_history
        if not msg.get("blocked", False)
    ]
    result = ask(question=req.question, chat_history=clean_history)
    return AskResponse(**result)


@router.post("/ingest")
async def trigger_ingest(req: IngestRequest):
    try:
        ingest(force=req.force)
        return {
            "status": "success",
            "populated": is_populated(),
            "message": "Knowledge base ingested successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
