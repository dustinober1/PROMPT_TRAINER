"""Metrics endpoints (Sprint 5 accuracy)."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import get_settings
from app.models.database import Evaluation

router = APIRouter()


@router.get("/accuracy")
async def get_accuracy(db: Session = Depends(get_db)):
    total_evaluations = db.query(Evaluation).count()
    reviewed = db.query(Evaluation).filter(Evaluation.is_correct.is_not(None)).count()
    correct = db.query(Evaluation).filter(Evaluation.is_correct.is_(True)).count()
    accuracy = (correct / reviewed * 100) if reviewed > 0 else None

    settings = get_settings()
    return {
        "total": reviewed,
        "pending": total_evaluations - reviewed,
        "correct": correct,
        "accuracy_percent": accuracy,
        "adapter": "ollama" if (settings.model_provider == "ollama" or settings.ollama_enabled) else "stub",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
