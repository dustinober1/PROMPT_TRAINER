"""Pydantic Schemas for Evaluations and Feedback."""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class RubricCriterionSummary(BaseModel):
    """Lightweight rubric criterion used in evaluation payloads."""
    id: int
    rubric_id: int
    name: str
    description: Optional[str] = None
    order: int

    model_config = {"from_attributes": True}


class FeedbackCreate(BaseModel):
    """Payload for creating or updating feedback on an evaluation."""
    criterion_id: Optional[int] = Field(None, description="Criterion being corrected (optional for overall feedback)")
    model_score: str = Field(..., description="Score returned by the model")
    user_corrected_score: str = Field(..., description="User-provided corrected score/value")
    user_explanation: Optional[str] = Field(None, description="Optional explanation of why the model was wrong")


class FeedbackResponse(BaseModel):
    """Response payload for stored feedback."""
    id: int
    evaluation_id: int
    rubric_id: int
    criterion_id: Optional[int] = None
    model_score: str
    user_corrected_score: str
    user_explanation: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class EvaluationCreate(BaseModel):
    """Request body for creating an evaluation"""
    paper_id: int = Field(..., description="Paper to evaluate")
    rubric_id: int = Field(..., description="Rubric used for evaluation")
    prompt_id: Optional[int] = Field(None, description="Prompt version to use (optional)")
    model_response: Optional[Any] = Field(
        None,
        description="Model response payload (JSON). If omitted, a stub is generated."
    )


class EvaluationResponse(BaseModel):
    """Response payload for an evaluation"""
    id: int
    paper_id: int
    paper_title: Optional[str] = None
    rubric_id: int
    rubric_name: Optional[str] = None
    rubric_scoring_type: Optional[str] = None
    prompt_id: int
    model_response: Any
    is_correct: Optional[bool]
    created_at: datetime
    feedback: List[FeedbackResponse] = Field(default_factory=list)
    rubric_criteria: List[RubricCriterionSummary] = Field(default_factory=list)

    model_config = {"from_attributes": True}
