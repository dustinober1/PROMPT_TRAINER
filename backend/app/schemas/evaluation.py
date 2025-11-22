"""
Pydantic Schemas for Evaluations

This stubbed version supports creating an evaluation record
using an optional prompt. If no prompt_id is supplied, a default
prompt is created automatically.
"""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


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
    prompt_id: int
    model_response: Any
    is_correct: Optional[bool]
    created_at: datetime

    model_config = {"from_attributes": True}
