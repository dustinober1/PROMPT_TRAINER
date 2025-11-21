"""
Rubric API Endpoints

Provides CRUD operations for rubrics and their criteria.

Available endpoints:
- POST   /api/rubrics/                - Create rubric with criteria
- GET    /api/rubrics/                - List all rubrics
- GET    /api/rubrics/{id}            - Get specific rubric with criteria
- PUT    /api/rubrics/{id}            - Update rubric metadata
- DELETE /api/rubrics/{id}            - Delete rubric and its criteria
- PUT    /api/rubrics/{id}/criteria/{criterion_id}  - Update criterion
- DELETE /api/rubrics/{id}/criteria/{criterion_id}  - Delete criterion

Tech Tip: This API handles NESTED resources.
Creating a rubric automatically creates all its criteria in one transaction.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.database import Rubric, Criterion
from app.schemas.rubric import (
    RubricCreate,
    RubricUpdate,
    RubricResponse,
    RubricList,
    CriterionUpdate,
    CriterionResponse
)

router = APIRouter()


@router.post("/", response_model=RubricResponse, status_code=status.HTTP_201_CREATED)
async def create_rubric(
    rubric: RubricCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new rubric with criteria.

    **Request Body:**
    - name: Rubric name
    - description: Optional description
    - scoring_type: "yes_no", "meets", or "numerical"
    - criteria: List of criteria (at least 1)

    **Returns:**
    - Complete rubric with all criteria and generated IDs

    **Example:**
    ```json
    {
        "name": "Essay Grading Rubric",
        "description": "Standard essay evaluation",
        "scoring_type": "yes_no",
        "criteria": [
            {"name": "Has thesis", "description": "Clear thesis statement", "order": 0},
            {"name": "Good grammar", "description": "Minimal errors", "order": 1}
        ]
    }
    ```

    Tech Tip: This creates the rubric AND all criteria in ONE database transaction.
    If anything fails, everything is rolled back (all-or-nothing).
    """
    # Create rubric instance
    db_rubric = Rubric(
        name=rubric.name,
        description=rubric.description,
        scoring_type=rubric.scoring_type
    )

    # Add to session and flush to get the ID
    # Tech Tip: flush() sends to DB but doesn't commit yet
    # This lets us get the rubric ID for the criteria
    db.add(db_rubric)
    db.flush()

    # Create all criteria
    for criterion_data in rubric.criteria:
        db_criterion = Criterion(
            rubric_id=db_rubric.id,
            name=criterion_data.name,
            description=criterion_data.description,
            order=criterion_data.order
        )
        db.add(db_criterion)

    # Commit everything at once
    db.commit()

    # Refresh to load all relationships
    db.refresh(db_rubric)

    return db_rubric


@router.get("/", response_model=List[RubricList])
async def list_rubrics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all rubrics with summary information.

    **Query Parameters:**
    - skip: Number to skip (pagination)
    - limit: Max results to return

    **Returns:**
    - List of rubrics with criteria count (not full criteria)

    Tech Tip: For list views, we return less data (criteria count)
    instead of full criteria. This makes the response faster
    when you have many rubrics.
    """
    rubrics = db.query(Rubric).offset(skip).limit(limit).all()

    # Transform to include criteria count
    result = []
    for rubric in rubrics:
        rubric_dict = {
            "id": rubric.id,
            "name": rubric.name,
            "description": rubric.description,
            "scoring_type": rubric.scoring_type,
            "created_at": rubric.created_at,
            "criteria_count": len(rubric.criteria)
        }
        result.append(RubricList(**rubric_dict))

    return result


@router.get("/{rubric_id}", response_model=RubricResponse)
async def get_rubric(
    rubric_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific rubric with all its criteria.

    **Path Parameters:**
    - rubric_id: ID of the rubric

    **Returns:**
    - Complete rubric with all criteria

    **Errors:**
    - 404: Rubric not found

    Tech Tip: SQLAlchemy automatically loads the criteria
    because of the relationship() we defined in the model.
    """
    rubric = db.query(Rubric).filter(Rubric.id == rubric_id).first()

    if not rubric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rubric with id {rubric_id} not found"
        )

    return rubric


@router.put("/{rubric_id}", response_model=RubricResponse)
async def update_rubric(
    rubric_id: int,
    rubric_update: RubricUpdate,
    db: Session = Depends(get_db)
):
    """
    Update rubric metadata (name, description, scoring_type).

    **Path Parameters:**
    - rubric_id: ID of the rubric to update

    **Request Body:**
    - name: New name (optional)
    - description: New description (optional)
    - scoring_type: New scoring type (optional)

    **Returns:**
    - Updated rubric with criteria

    **Errors:**
    - 404: Rubric not found

    Tech Tip: This only updates the rubric itself, not criteria.
    Use the criteria endpoints to modify individual criteria.
    """
    rubric = db.query(Rubric).filter(Rubric.id == rubric_id).first()

    if not rubric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rubric with id {rubric_id} not found"
        )

    # Update provided fields
    update_data = rubric_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rubric, field, value)

    db.commit()
    db.refresh(rubric)

    return rubric


@router.delete("/{rubric_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rubric(
    rubric_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a rubric and all its criteria.

    **Path Parameters:**
    - rubric_id: ID of the rubric to delete

    **Returns:**
    - 204 No Content

    **Errors:**
    - 404: Rubric not found

    **Warning:**
    - Deletes ALL criteria (CASCADE)
    - Deletes ALL evaluations using this rubric (CASCADE)

    Tech Tip: Because of CASCADE in the database schema,
    deleting a rubric automatically deletes all its criteria.
    """
    rubric = db.query(Rubric).filter(Rubric.id == rubric_id).first()

    if not rubric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rubric with id {rubric_id} not found"
        )

    db.delete(rubric)
    db.commit()

    return None


# ==================== CRITERION MANAGEMENT ====================

@router.put("/{rubric_id}/criteria/{criterion_id}", response_model=CriterionResponse)
async def update_criterion(
    rubric_id: int,
    criterion_id: int,
    criterion_update: CriterionUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a specific criterion.

    **Path Parameters:**
    - rubric_id: ID of the rubric (for verification)
    - criterion_id: ID of the criterion to update

    **Request Body:**
    - name: New name (optional)
    - description: New description (optional)
    - order: New order (optional)

    **Returns:**
    - Updated criterion

    **Errors:**
    - 404: Criterion not found or doesn't belong to this rubric

    Tech Tip: We verify the criterion belongs to the specified rubric
    to prevent accidentally modifying criteria from other rubrics.
    """
    criterion = db.query(Criterion).filter(
        Criterion.id == criterion_id,
        Criterion.rubric_id == rubric_id
    ).first()

    if not criterion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Criterion {criterion_id} not found in rubric {rubric_id}"
        )

    # Update provided fields
    update_data = criterion_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(criterion, field, value)

    db.commit()
    db.refresh(criterion)

    return criterion


@router.delete("/{rubric_id}/criteria/{criterion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_criterion(
    rubric_id: int,
    criterion_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific criterion from a rubric.

    **Path Parameters:**
    - rubric_id: ID of the rubric
    - criterion_id: ID of the criterion to delete

    **Returns:**
    - 204 No Content

    **Errors:**
    - 404: Criterion not found
    - 400: Cannot delete last criterion (rubric must have at least 1)

    Tech Tip: We prevent deleting the last criterion because
    a rubric without criteria doesn't make sense.
    """
    # First verify rubric exists
    rubric = db.query(Rubric).filter(Rubric.id == rubric_id).first()
    if not rubric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rubric {rubric_id} not found"
        )

    # Check if this is the last criterion
    if len(rubric.criteria) <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the last criterion. Rubric must have at least one criterion."
        )

    # Find and delete criterion
    criterion = db.query(Criterion).filter(
        Criterion.id == criterion_id,
        Criterion.rubric_id == rubric_id
    ).first()

    if not criterion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Criterion {criterion_id} not found in rubric {rubric_id}"
        )

    db.delete(criterion)
    db.commit()

    return None


# Tech Tip: Nested Resource URLs
#
# RESTful convention for nested resources:
#   /api/rubrics/               - Work with rubrics
#   /api/rubrics/{id}           - Specific rubric
#   /api/rubrics/{id}/criteria  - Criteria within a rubric
#   /api/rubrics/{id}/criteria/{criterion_id}  - Specific criterion
#
# This URL structure makes it clear that criteria belong to rubrics.
