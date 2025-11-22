"""
Schemas for prompt versioning.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PromptCreate(BaseModel):
    template_text: str = Field(..., min_length=1)
    parent_version_id: Optional[int] = Field(None, description="Parent prompt id, if any")
    is_active: bool = True


class PromptResponse(BaseModel):
    id: int
    version: int
    template_text: str
    parent_version_id: Optional[int]
    created_at: datetime
    is_active: bool

    model_config = {"from_attributes": True}
