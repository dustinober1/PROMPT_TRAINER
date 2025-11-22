"""Evaluation API Endpoints (Sprint 4: results + feedback)."""

import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.database import Evaluation, Paper, Rubric, Prompt, Criterion, FeedbackEntry
from app.schemas.evaluation import (
    EvaluationCreate,
    EvaluationResponse,
    FeedbackCreate,
    FeedbackResponse,
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
        template_text="Evaluate {{paper_content}} using rubric {{rubric}}",
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


def _parse_model_response(model_response):
    """Safely parse model_response stored as text into JSON/dict for responses."""
    if isinstance(model_response, (dict, list)):
        return model_response
    if not model_response:
        return None
    try:
        return json.loads(model_response)
    except Exception:
        return model_response


def _serialize_feedback(entry: FeedbackEntry) -> dict:
    """Shape feedback entries for API responses."""
    return {
        "id": entry.id,
        "evaluation_id": entry.evaluation_id,
        "rubric_id": entry.rubric_id,
        "criterion_id": entry.criterion_id,
        "model_score": entry.model_score,
        "user_corrected_score": entry.user_corrected_score,
        "user_explanation": entry.user_explanation,
        "created_at": entry.created_at,
    }


def _serialize_evaluation(evaluation: Evaluation, include_feedback: bool = True) -> dict:
    """Attach related names, parsed model_response, rubric criteria, and feedback."""
    model_response = _parse_model_response(evaluation.model_response)
    rubric = evaluation.rubric
    paper = evaluation.paper
    feedback_entries = evaluation.feedback_entries if include_feedback else []

    criteria = []
    if rubric:
        criteria = [
            {
                "id": c.id,
                "rubric_id": c.rubric_id,
                "name": c.name,
                "description": c.description,
                "order": c.order,
                "min_score": c.min_score,
                "max_score": c.max_score,
            }
            for c in sorted(rubric.criteria, key=lambda c: c.order)
        ]

    return {
        "id": evaluation.id,
        "paper_id": evaluation.paper_id,
        "paper_title": paper.title if paper else None,
        "rubric_id": evaluation.rubric_id,
        "rubric_name": rubric.name if rubric else None,
        "rubric_scoring_type": rubric.scoring_type if rubric else None,
        "prompt_id": evaluation.prompt_id,
        "model_response": model_response,
        "is_correct": evaluation.is_correct,
        "created_at": evaluation.created_at,
        "feedback": [_serialize_feedback(entry) for entry in feedback_entries],
        "rubric_criteria": criteria,
    }


def _validate_corrected_score(rubric: Rubric, corrected_score: str, criterion: Optional[Criterion] = None):
    """
    Ensure corrected score fits rubric scoring type.

    Tech Tip: Different scoring types require different validation:
    - yes_no: Must be 'yes' or 'no'
    - meets_not_meets: Must be 'meets' or 'does_not_meet'
    - numerical: Must be an integer within criterion's min/max range
    """
    if rubric.scoring_type == "yes_no":
        normalized = corrected_score.strip().lower()
        if normalized not in {"yes", "no"}:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="For yes/no rubrics, corrected score must be 'yes' or 'no'.",
            )
        return normalized

    elif rubric.scoring_type == "meets_not_meets":
        normalized = corrected_score.strip().lower()
        if normalized not in {"meets", "does_not_meet"}:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="For meets/not-meets rubrics, corrected score must be 'meets' or 'does_not_meet'.",
            )
        return normalized

    elif rubric.scoring_type == "numerical":
        try:
            score = int(corrected_score.strip())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="For numerical rubrics, corrected score must be an integer.",
            )

        # Validate against criterion's range if criterion is provided
        if criterion:
            if criterion.min_score is not None and score < criterion.min_score:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail=f"Score {score} is below minimum {criterion.min_score}.",
                )
            if criterion.max_score is not None and score > criterion.max_score:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail=f"Score {score} is above maximum {criterion.max_score}.",
                )

        return str(score)  # Return as string to maintain consistency

    return corrected_score.strip()


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
    # Tech Tip: Pass complete rubric data including scoring_type and criterion details
    adapter = get_adapter()
    try:
        model_response = payload.model_response or adapter.evaluate(
            paper_content=paper.content,
            rubric={
                "id": rubric.id,
                "name": rubric.name,
                "scoring_type": rubric.scoring_type,
                "criteria": [
                    {
                        "id": c.id,
                        "name": c.name,
                        "description": c.description,
                        "min_score": c.min_score,
                        "max_score": c.max_score,
                    }
                    for c in rubric.criteria
                ],
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

    return _serialize_evaluation(evaluation)


@router.get("/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """Fetch a single evaluation with rubric criteria and feedback."""
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation not found")
    return _serialize_evaluation(evaluation)


@router.get("/", response_model=List[EvaluationResponse])
async def list_evaluations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List evaluations with parsed model_response."""
    evaluations = db.query(Evaluation).offset(skip).limit(limit).all()
    return [_serialize_evaluation(ev) for ev in evaluations]


@router.get("/{evaluation_id}/feedback", response_model=List[FeedbackResponse])
async def list_feedback(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """List feedback entries for an evaluation."""
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation not found")
    return [_serialize_feedback(entry) for entry in evaluation.feedback_entries]


@router.post("/{evaluation_id}/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_feedback(
    evaluation_id: int,
    payload: FeedbackCreate,
    db: Session = Depends(get_db)
):
    """Create or update feedback for a specific evaluation + criterion."""
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation not found")

    rubric = evaluation.rubric
    if not rubric:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rubric not found for evaluation")

    criterion: Optional[Criterion] = None
    if payload.criterion_id is not None:
        criterion = db.query(Criterion).filter(Criterion.id == payload.criterion_id).first()
        if not criterion:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Criterion not found")
        if criterion.rubric_id != rubric.id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Criterion does not belong to evaluation rubric",
            )

    corrected_score = _validate_corrected_score(rubric, payload.user_corrected_score, criterion)
    existing = (
        db.query(FeedbackEntry)
        .filter(
            FeedbackEntry.evaluation_id == evaluation.id,
            FeedbackEntry.criterion_id == payload.criterion_id,
        )
        .first()
    )

    if existing:
        existing.model_score = payload.model_score.strip()
        existing.user_corrected_score = corrected_score
        existing.user_explanation = payload.user_explanation
        entry = existing
    else:
        entry = FeedbackEntry(
            evaluation_id=evaluation.id,
            rubric_id=rubric.id,
            criterion_id=payload.criterion_id,
            model_score=payload.model_score.strip(),
            user_corrected_score=corrected_score,
            user_explanation=payload.user_explanation,
        )
        db.add(entry)

    # User provided corrections, so flag evaluation as incorrect unless explicitly set later
    evaluation.is_correct = False

    db.commit()
    db.refresh(entry)
    db.refresh(evaluation)
    return _serialize_feedback(entry)


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
    return _serialize_evaluation(evaluation)
