"""
Prompt API Endpoints (minimal)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.database import Prompt
from app.schemas.prompt import PromptCreate, PromptResponse

router = APIRouter()


@router.post("/", response_model=PromptResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt(payload: PromptCreate, db: Session = Depends(get_db)):
    parent_id = payload.parent_version_id
    if parent_id:
        parent = db.query(Prompt).filter(Prompt.id == parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail=f"Parent prompt {parent_id} not found")
        version = (parent.version or 0) + 1
    else:
        latest = db.query(Prompt).order_by(Prompt.version.desc()).first()
        version = (latest.version if latest else 0) + 1

    prompt = Prompt(
        version=version,
        template_text=payload.template_text,
        parent_version_id=parent_id,
        is_active=payload.is_active,
    )
    db.add(prompt)

    # ensure only one active prompt
    if payload.is_active:
        db.query(Prompt).filter(Prompt.id != prompt.id).update({"is_active": False})

    db.commit()
    db.refresh(prompt)
    return prompt


@router.get("/", response_model=List[PromptResponse])
async def list_prompts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    prompts = db.query(Prompt).order_by(Prompt.created_at.desc()).offset(skip).limit(limit).all()
    return prompts
