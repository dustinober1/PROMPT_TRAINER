"""Prompt API Endpoints (Sprint 5 - versioning + manual editor)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.database import Prompt
from app.schemas.prompt import PromptCreate, PromptResponse, PromptUpdate
from app.services.sanitization import sanitize_text

router = APIRouter()

REQUIRED_PLACEHOLDERS = ["{{paper_content}}", "{{rubric}}"]


def _validate_placeholders(template_text: str):
    for placeholder in REQUIRED_PLACEHOLDERS:
        if placeholder not in template_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Prompt must include placeholder {placeholder}",
            )


def _ensure_single_active(db: Session, active_prompt_id: Optional[int] = None):
    """Deactivate all prompts except optional active id."""
    query = db.query(Prompt)
    if active_prompt_id is not None:
        query = query.filter(Prompt.id != active_prompt_id)
    query.update({"is_active": False})


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

    template_text = sanitize_text(payload.template_text, "Prompt template", min_length=1, max_length=10000)
    _validate_placeholders(template_text)

    prompt = Prompt(
        version=version,
        template_text=template_text,
        parent_version_id=parent_id,
        is_active=payload.is_active,
    )
    db.add(prompt)
    db.flush()

    if payload.is_active:
        _ensure_single_active(db, active_prompt_id=prompt.id)

    db.commit()
    db.refresh(prompt)
    return prompt


@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(prompt_id: int, payload: PromptUpdate, db: Session = Depends(get_db)):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "template_text" in update_data:
        template_text = sanitize_text(update_data["template_text"], "Prompt template", min_length=1, max_length=10000)
        _validate_placeholders(template_text)
        prompt.template_text = template_text
    if "is_active" in update_data and update_data["is_active"]:
        _ensure_single_active(db, active_prompt_id=prompt.id)
        prompt.is_active = True
    elif "is_active" in update_data:
        prompt.is_active = update_data["is_active"]

    db.commit()
    db.refresh(prompt)
    return prompt


@router.post("/{prompt_id}/activate", response_model=PromptResponse)
async def activate_prompt(prompt_id: int, db: Session = Depends(get_db)):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    _ensure_single_active(db, active_prompt_id=prompt.id)
    prompt.is_active = True
    db.commit()
    db.refresh(prompt)
    return prompt


@router.get("/", response_model=List[PromptResponse])
async def list_prompts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    prompts = db.query(Prompt).order_by(Prompt.created_at.desc()).offset(skip).limit(limit).all()
    return prompts


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(prompt_id: int, db: Session = Depends(get_db)):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt
