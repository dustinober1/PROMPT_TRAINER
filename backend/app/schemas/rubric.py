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

    - YES_NO: Simple binary scoring (yes/no)
    - MEETS_NOT_MEETS: Standards-based grading (meets standard or does not meet)
    - NUMERICAL: Point-based scoring with min/max range (e.g., 0-10 points)
    """
    YES_NO = "yes_no"
    MEETS_NOT_MEETS = "meets_not_meets"
    NUMERICAL = "numerical"


# ==================== CRITERION SCHEMAS ====================

class CriterionBase(BaseModel):
    """
    Base criterion fields (shared across schemas).

    Tech Tip: Criteria can have optional min/max scores for numerical rubrics.
    When the parent rubric uses numerical scoring, these fields become required.
    """
    name: str = Field(..., min_length=1, max_length=255, description="Criterion name")
    description: Optional[str] = Field(None, max_length=2000, description="Detailed description of what to evaluate")
    order: int = Field(0, ge=0, description="Display order (0-based)")
    min_score: Optional[int] = Field(None, description="Minimum score for numerical rubrics")
    max_score: Optional[int] = Field(None, description="Maximum score for numerical rubrics")

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Ensure name isn't just whitespace"""
        if not v.strip():
            raise ValueError('Criterion name cannot be empty or only whitespace')
        return v.strip()

    @field_validator('description')
    @classmethod
    def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
        """
        Sanitize description field.

        Tech Tip: This prevents XSS attacks by rejecting script tags.
        Sprint 5 added this security layer across all text inputs.
        """
        if v is None:
            return None
        # Reject script tags
        if '<script' in v.lower() or '</script>' in v.lower():
            raise ValueError('Description cannot contain script tags')
        # Strip excess whitespace
        v = v.strip()
        return v if v else None


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
    description: Optional[str] = Field(None, max_length=2000)
    order: Optional[int] = Field(None, ge=0)
    min_score: Optional[int] = None
    max_score: Optional[int] = None

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Criterion name cannot be empty')
        return v.strip() if v else None

    @field_validator('description')
    @classmethod
    def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize description field"""
        if v is None:
            return None
        if '<script' in v.lower() or '</script>' in v.lower():
            raise ValueError('Description cannot contain script tags')
        v = v.strip()
        return v if v else None


class CriterionResponse(CriterionBase):
    """
    Complete criterion data returned by API.
    Includes the database-generated ID.

    Tech Tip: This inherits all fields from CriterionBase (name, description, order, min_score, max_score)
    and adds the database fields (id, rubric_id).
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

    def validate_numerical_scoring(self):
        """
        Validate that numerical rubrics have proper min/max scores.

        Tech Tip: This is called after the model is created, not as a @field_validator,
        because we need to check scoring_type against criteria fields.
        """
        if self.scoring_type == ScoringType.NUMERICAL:
            for i, criterion in enumerate(self.criteria):
                # Check that min_score and max_score are provided
                if criterion.min_score is None:
                    raise ValueError(f'Criterion "{criterion.name}" requires min_score for numerical rubrics')
                if criterion.max_score is None:
                    raise ValueError(f'Criterion "{criterion.name}" requires max_score for numerical rubrics')

                # Check that min < max
                if criterion.min_score >= criterion.max_score:
                    raise ValueError(
                        f'Criterion "{criterion.name}": min_score ({criterion.min_score}) '
                        f'must be less than max_score ({criterion.max_score})'
                    )

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
