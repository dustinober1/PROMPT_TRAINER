"""
Pydantic Schemas for Rubrics and Criteria

Rubrics have a one-to-many relationship with Criteria:
- One Rubric contains multiple Criteria
- When creating a Rubric, we create all Criteria at once (nested creation)

Tech Tip: Nested schemas allow creating complex objects in a single API call.
Instead of: Create rubric → Create criterion 1 → Create criterion 2 → ...
You do: Create rubric with all criteria in one request!
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List, Optional
from enum import Enum


# Enum for valid scoring types
class ScoringType(str, Enum):
    """
    Valid scoring types for rubrics.

    Tech Tip: Using an Enum ensures only valid values are accepted.
    FastAPI will reject any other values automatically.
    """
    YES_NO = "yes_no"
    MEETS = "meets"
    NUMERICAL = "numerical"


# ==================== CRITERION SCHEMAS ====================

class CriterionBase(BaseModel):
    """Base criterion fields (shared across schemas)"""
    name: str = Field(..., min_length=1, max_length=255, description="Criterion name")
    description: Optional[str] = Field(None, description="Detailed description of what to evaluate")
    order: int = Field(0, ge=0, description="Display order (0-based)")

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Ensure name isn't just whitespace"""
        if not v.strip():
            raise ValueError('Criterion name cannot be empty or only whitespace')
        return v.strip()


class CriterionCreate(CriterionBase):
    """
    Data for creating a criterion.

    Used when creating a rubric with nested criteria.
    Note: rubric_id is NOT included - it's set automatically.
    """
    pass


class CriterionUpdate(BaseModel):
    """
    Data for updating a criterion.
    All fields are optional for partial updates.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    order: Optional[int] = Field(None, ge=0)

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Criterion name cannot be empty')
        return v.strip() if v else None


class CriterionResponse(CriterionBase):
    """
    Complete criterion data returned by API.
    Includes the database-generated ID.
    """
    id: int
    rubric_id: int

    model_config = {
        "from_attributes": True
    }


# ==================== RUBRIC SCHEMAS ====================

class RubricBase(BaseModel):
    """Base rubric fields"""
    name: str = Field(..., min_length=1, max_length=255, description="Rubric name")
    description: Optional[str] = Field(None, description="What this rubric is for")
    scoring_type: ScoringType = Field(..., description="How criteria are scored")

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Rubric name cannot be empty or only whitespace')
        return v.strip()


class RubricCreate(RubricBase):
    """
    Data for creating a new rubric with criteria.

    Tech Tip: This is a NESTED schema!
    The 'criteria' field is a list of CriterionCreate objects.

    Example request:
    {
        "name": "Essay Grading Rubric",
        "description": "Standard essay evaluation",
        "scoring_type": "yes_no",
        "criteria": [
            {"name": "Has thesis statement", "description": "Clear, specific thesis", "order": 0},
            {"name": "Proper grammar", "description": "No major grammatical errors", "order": 1},
            {"name": "Cites sources", "description": "At least 3 sources cited", "order": 2}
        ]
    }
    """
    criteria: List[CriterionCreate] = Field(
        ...,
        min_length=1,
        description="List of criteria (at least 1 required)"
    )

    @field_validator('criteria')
    @classmethod
    def validate_criteria_order(cls, v: List[CriterionCreate]) -> List[CriterionCreate]:
        """Ensure order numbers are unique within the rubric"""
        orders = [c.order for c in v]
        if len(orders) != len(set(orders)):
            # Auto-fix: assign sequential order numbers
            for i, criterion in enumerate(v):
                criterion.order = i
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Essay Grading Rubric",
                    "description": "Standard 5-paragraph essay evaluation",
                    "scoring_type": "yes_no",
                    "criteria": [
                        {
                            "name": "Has clear thesis statement",
                            "description": "Thesis is specific and arguable",
                            "order": 0
                        },
                        {
                            "name": "Proper grammar and spelling",
                            "description": "Minimal grammatical errors",
                            "order": 1
                        },
                        {
                            "name": "Cites credible sources",
                            "description": "At least 3 credible sources cited",
                            "order": 2
                        }
                    ]
                }
            ]
        }
    }


class RubricUpdate(BaseModel):
    """
    Data for updating a rubric.

    Tech Tip: Criteria are updated separately through their own endpoints.
    This prevents accidentally deleting criteria when updating rubric metadata.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    scoring_type: Optional[ScoringType] = None

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Rubric name cannot be empty')
        return v.strip() if v else None


class RubricResponse(RubricBase):
    """
    Complete rubric data with all criteria.

    Tech Tip: This is also NESTED!
    When you fetch a rubric, you get all its criteria automatically.
    """
    id: int
    created_at: datetime
    criteria: List[CriterionResponse] = Field(default_factory=list)

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "name": "Essay Grading Rubric",
                    "description": "Standard essay evaluation",
                    "scoring_type": "yes_no",
                    "created_at": "2025-11-21T18:00:00",
                    "criteria": [
                        {
                            "id": 1,
                            "rubric_id": 1,
                            "name": "Has clear thesis statement",
                            "description": "Thesis is specific and arguable",
                            "order": 0
                        },
                        {
                            "id": 2,
                            "rubric_id": 1,
                            "name": "Proper grammar and spelling",
                            "description": "Minimal grammatical errors",
                            "order": 1
                        }
                    ]
                }
            ]
        }
    }


class RubricList(BaseModel):
    """
    Abbreviated rubric data for list views.

    Shows criterion count instead of full criteria.
    """
    id: int
    name: str
    description: Optional[str]
    scoring_type: ScoringType
    created_at: datetime
    criteria_count: int = Field(0, description="Number of criteria in this rubric")

    model_config = {
        "from_attributes": True
    }


# Tech Tip: Nested Schema Benefits
#
# Instead of multiple API calls:
#   POST /api/rubrics/ → {id: 1}
#   POST /api/criteria/ → {rubric_id: 1, name: "Thesis"}
#   POST /api/criteria/ → {rubric_id: 1, name: "Grammar"}
#
# You make ONE call:
#   POST /api/rubrics/ → {
#     name: "Essay Rubric",
#     criteria: [{name: "Thesis"}, {name: "Grammar"}]
#   }
#
# This is:
# - Faster (1 request instead of 3)
# - Safer (all-or-nothing transaction)
# - Easier (simpler client code)
