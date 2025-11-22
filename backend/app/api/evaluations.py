"""
Evaluation API Endpoints (stubbed)

Creates evaluation records using papers and rubrics. If no prompt_id
is supplied, a default prompt is created automatically.
"""

import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.database import Evaluation, Paper, Rubric, Prompt
from app.schemas.evaluation import (
    EvaluationCreate,
    EvaluationResponse,
)
from app.services.model_adapter import get_adapter

router = APIRouter()


def _get_or_create_default_prompt(db: Session) -> Prompt:
    """Ensure at least one prompt exists and return it."""
    prompt = db.query(Prompt).order_by(Prompt.id.asc()).first()
    if prompt:
        return prompt

    prompt = Prompt(
        version=1,
        template_text="Default evaluation prompt (stub)",
        parent_version_id=None,
        is_active=True,
        accuracy_rate=None,
        total_evaluations=0,
    )
    db.add(prompt)
    db.flush()
    return prompt


def _build_stub_response(rubric: Rubric) -> str:
    """Generate a simple stub response matching rubric criteria."""
    criteria = rubric.criteria or []
    entries = [
        {
            "criterion_id": c.id,
            "criterion_name": c.name,
            "score": "yes",
            "reasoning": "Stubbed evaluation response",
        }
        for c in criteria
    ]
    return {"evaluations": entries}


@router.post("/", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED)
async def create_evaluation(
    payload: EvaluationCreate,
    db: Session = Depends(get_db)
):
    """Create a stubbed evaluation record."""
    paper = db.query(Paper).filter(Paper.id == payload.paper_id).first()
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper with id {payload.paper_id} not found"
        )

    rubric = db.query(Rubric).filter(Rubric.id == payload.rubric_id).first()
    if not rubric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rubric with id {payload.rubric_id} not found"
        )

    prompt: Prompt
    if payload.prompt_id is not None:
        prompt = db.query(Prompt).filter(Prompt.id == payload.prompt_id).first()
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prompt with id {payload.prompt_id} not found"
            )
    else:
        prompt = _get_or_create_default_prompt(db)

    # Evaluate via adapter (configurable; defaults to stub)
    adapter = get_adapter()
    try:
        model_response = payload.model_response or adapter.evaluate(
            paper_content=paper.content,
            rubric={
                "id": rubric.id,
                "name": rubric.name,
                "criteria": [{"id": c.id, "name": c.name} for c in rubric.criteria],
            },
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    evaluation = Evaluation(
        paper_id=paper.id,
        rubric_id=rubric.id,
        prompt_id=prompt.id,
        model_response=json.dumps(model_response),
        is_correct=None,
    )
    db.add(evaluation)

    # increment prompt stats
    prompt.total_evaluations = (prompt.total_evaluations or 0) + 1

    db.commit()
    db.refresh(evaluation)
    db.refresh(prompt)

    # Return with parsed model_response and names attached
    evaluation.model_response = model_response
    evaluation.paper_title = paper.title
    evaluation.rubric_name = rubric.name
    return evaluation


@router.get("/", response_model=List[EvaluationResponse])
async def list_evaluations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List evaluations with parsed model_response."""
    evaluations = db.query(Evaluation).offset(skip).limit(limit).all()
    for ev in evaluations:
        try:
            ev.model_response = json.loads(ev.model_response) if ev.model_response else None
        except Exception:
            # leave as-is if parsing fails
            pass
        ev.paper_title = ev.paper.title if ev.paper else None
        ev.rubric_name = ev.rubric.name if ev.rubric else None
    return evaluations


@router.patch("/{evaluation_id}/feedback", response_model=EvaluationResponse)
async def update_feedback(
    evaluation_id: int,
    is_correct: bool,
    db: Session = Depends(get_db)
):
    """Update evaluation correctness (feedback)."""
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    evaluation.is_correct = is_correct
    db.commit()
    db.refresh(evaluation)
    try:
        evaluation.model_response = json.loads(evaluation.model_response) if evaluation.model_response else None
    except Exception:
        pass
    evaluation.paper_title = evaluation.paper.title if evaluation.paper else None
    evaluation.rubric_name = evaluation.rubric.name if evaluation.rubric else None
    return evaluation
