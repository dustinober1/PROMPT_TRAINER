"""
Pydantic Schemas for Papers

Schemas define the structure of data for API requests and responses.
They provide:
1. Data validation (automatic type checking)
2. JSON serialization (convert Python objects to JSON)
3. API documentation (shown in /docs)

Tech Tip: The difference between Models and Schemas:
- Models (SQLAlchemy) = Database tables (what's stored)
- Schemas (Pydantic) = API data format (what's sent/received)
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


# Schema for creating a new paper (request body)
class PaperCreate(BaseModel):
    """
    Data required to create a new paper.

    Used in: POST /api/papers/

    Example request body:
    {
        "title": "My Essay on Climate Change",
        "content": "Climate change is one of the most pressing..."
    }
    """
    title: str = Field(..., min_length=1, max_length=255, description="Paper title")
    content: str = Field(..., min_length=10, description="Paper content (minimum 10 characters)")

    # Validator to ensure title isn't just whitespace
    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Ensure title contains more than just spaces"""
        if not v.strip():
            raise ValueError('Title cannot be empty or only whitespace')
        return v.strip()

    # Validator for content
    @field_validator('content')
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        """Ensure content is substantial"""
        if not v.strip():
            raise ValueError('Content cannot be empty or only whitespace')
        if len(v.strip()) < 10:
            raise ValueError('Content must be at least 10 characters')
        return v.strip()

    # Example for API docs
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "The Impact of AI on Education",
                    "content": "Artificial Intelligence is transforming education in unprecedented ways. From personalized learning experiences to automated grading systems, AI technologies are reshaping how students learn and teachers teach."
                }
            ]
        }
    }


# Schema for updating a paper (optional fields)
class PaperUpdate(BaseModel):
    """
    Data for updating an existing paper.

    Used in: PUT /api/papers/{id}

    All fields are optional - only provided fields will be updated.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=10)

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty or only whitespace')
        return v.strip() if v else None

    @field_validator('content')
    @classmethod
    def content_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError('Content cannot be empty')
            if len(v.strip()) < 10:
                raise ValueError('Content must be at least 10 characters')
        return v.strip() if v else None


# Schema for paper response (what API returns)
class PaperResponse(BaseModel):
    """
    Complete paper data returned by the API.

    Used in: GET /api/papers/{id}, POST /api/papers/

    Tech Tip: model_config with from_attributes=True allows
    converting SQLAlchemy models directly to Pydantic schemas.
    """
    id: int
    title: str
    content: str
    submission_date: datetime
    created_at: datetime

    model_config = {
        "from_attributes": True,  # Allows: PaperResponse.model_validate(db_paper)
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "title": "The Impact of AI on Education",
                    "content": "Artificial Intelligence is transforming education...",
                    "submission_date": "2025-11-21T17:30:00",
                    "created_at": "2025-11-21T17:30:00"
                }
            ]
        }
    }


# Schema for listing papers (less detail, optimized for lists)
class PaperList(BaseModel):
    """
    Abbreviated paper data for list views.

    Used in: GET /api/papers/ (list all papers)

    Shows a preview instead of full content to reduce response size.
    """
    id: int
    title: str
    content_preview: str = Field(..., description="First 150 characters of content")
    submission_date: datetime

    model_config = {
        "from_attributes": True
    }


# Schema for paper with evaluation count
class PaperWithStats(PaperResponse):
    """
    Paper data with additional statistics.

    Future use: Show how many times a paper has been evaluated.
    """
    evaluation_count: int = Field(0, description="Number of evaluations for this paper")


# Tech Tip: Why separate Create, Update, and Response schemas?
#
# PaperCreate:
#   - User provides: title, content
#   - Database generates: id, dates
#
# PaperUpdate:
#   - All fields optional (partial updates)
#   - Can update just title, just content, or both
#
# PaperResponse:
#   - Includes everything (id, dates, etc.)
#   - What users see after creating/fetching
#
# This separation makes the API intuitive:
#   POST /papers/ → requires PaperCreate
#   GET /papers/1 → returns PaperResponse
#   PUT /papers/1 → accepts PaperUpdate
