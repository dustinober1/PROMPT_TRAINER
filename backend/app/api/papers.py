"""
Paper API Endpoints

This module provides CRUD (Create, Read, Update, Delete) operations for papers.

Available endpoints:
- POST   /api/papers/          - Create a new paper
- GET    /api/papers/          - List all papers
- GET    /api/papers/{id}      - Get a specific paper
- PUT    /api/papers/{id}      - Update a paper
- DELETE /api/papers/{id}      - Delete a paper

Tech Tip: FastAPI automatically:
1. Validates request data using Pydantic schemas
2. Generates interactive API docs at /docs
3. Handles JSON serialization
4. Provides helpful error messages
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.database import Paper, Rubric
from app.schemas.paper import PaperCreate, PaperUpdate, PaperResponse, PaperList

# Create router for paper endpoints
# Tech Tip: Routers group related endpoints together
router = APIRouter()


@router.post("/", response_model=PaperResponse, status_code=status.HTTP_201_CREATED)
async def create_paper(
    paper: PaperCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new paper.

    **Request Body:**
    - title: Paper title (1-255 characters)
    - content: Paper content (minimum 10 characters)

    **Returns:**
    - Complete paper object with generated ID and timestamps

    **Example:**
    ```json
    {
        "title": "My Essay on Climate Change",
        "content": "Climate change is one of the most pressing issues..."
    }
    ```

    Tech Tip: FastAPI automatically validates the request body
    against PaperCreate schema before this function runs.
    """
    # Validate rubric if provided
    if paper.rubric_id is not None:
        rubric = db.query(Rubric).filter(Rubric.id == paper.rubric_id).first()
        if not rubric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rubric with id {paper.rubric_id} not found"
            )

    # Create new Paper instance from request data
    db_paper = Paper(
        title=paper.title,
        content=paper.content,
        rubric_id=paper.rubric_id
        # submission_date and created_at are set automatically by database defaults
    )

    # Add to database session (like adding to shopping cart)
    db.add(db_paper)

    # Commit transaction (save to database)
    db.commit()

    # Refresh to get auto-generated fields (id, dates)
    db.refresh(db_paper)

    # FastAPI automatically converts to JSON using PaperResponse schema
    return db_paper


@router.get("/", response_model=List[PaperList])
async def list_papers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all papers with pagination.

    **Query Parameters:**
    - skip: Number of papers to skip (default: 0)
    - limit: Maximum number of papers to return (default: 100)

    **Returns:**
    - List of papers with content previews

    **Example:**
    ```
    GET /api/papers/?skip=0&limit=10
    ```

    Tech Tip: Pagination prevents loading too much data at once.
    For 1000 papers, you can load 100 at a time.
    """
    # Query database for papers
    # Tech Tip: offset() = skip, limit() = max results
    papers = db.query(Paper).offset(skip).limit(limit).all()

    # Transform papers to include content preview
    result = []
    for paper in papers:
        paper_dict = {
            "id": paper.id,
            "title": paper.title,
            "rubric_id": paper.rubric_id,
            "rubric_name": paper.rubric_name,
            "content_preview": paper.content[:150] + "..." if len(paper.content) > 150 else paper.content,
            "submission_date": paper.submission_date
        }
        result.append(PaperList(**paper_dict))

    return result


@router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper(
    paper_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific paper by ID.

    **Path Parameters:**
    - paper_id: ID of the paper to retrieve

    **Returns:**
    - Complete paper object

    **Errors:**
    - 404: Paper not found

    Tech Tip: {paper_id} in the path is automatically converted to int
    and passed to this function.
    """
    # Query for paper by ID
    paper = db.query(Paper).filter(Paper.id == paper_id).first()

    # Return 404 if not found
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper with id {paper_id} not found"
        )

    return paper


@router.put("/{paper_id}", response_model=PaperResponse)
async def update_paper(
    paper_id: int,
    paper_update: PaperUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing paper.

    **Path Parameters:**
    - paper_id: ID of the paper to update

    **Request Body:**
    - title: New title (optional)
    - content: New content (optional)

    **Returns:**
    - Updated paper object

    **Errors:**
    - 404: Paper not found

    **Example:**
    ```json
    {
        "title": "Updated Title"
    }
    ```

    Tech Tip: Only fields provided in the request will be updated.
    This is called a "partial update" or PATCH-like behavior.
    """
    # Find existing paper
    paper = db.query(Paper).filter(Paper.id == paper_id).first()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper with id {paper_id} not found"
        )

    # Update only provided fields
    # Tech Tip: exclude_unset=True ignores fields not in request
    update_data = paper_update.model_dump(exclude_unset=True)

    if "rubric_id" in update_data:
        rubric_id = update_data.pop("rubric_id")
        if rubric_id is not None:
            rubric = db.query(Rubric).filter(Rubric.id == rubric_id).first()
            if not rubric:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Rubric with id {rubric_id} not found"
                )
        paper.rubric_id = rubric_id

    for field, value in update_data.items():
        setattr(paper, field, value)

    # Save changes
    db.commit()
    db.refresh(paper)

    return paper


@router.delete("/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_paper(
    paper_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a paper.

    **Path Parameters:**
    - paper_id: ID of the paper to delete

    **Returns:**
    - 204 No Content (successful deletion returns no body)

    **Errors:**
    - 404: Paper not found

    **Warning:**
    This will also delete all associated evaluations due to CASCADE.

    Tech Tip: HTTP 204 means "success, but no content to return"
    This is standard for DELETE operations.
    """
    # Find paper
    paper = db.query(Paper).filter(Paper.id == paper_id).first()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper with id {paper_id} not found"
        )

    # Delete from database
    db.delete(paper)
    db.commit()

    # Return None for 204 No Content
    return None


# Tech Tip: How FastAPI routing works
#
# 1. Request comes in: POST /api/papers/
# 2. FastAPI finds matching route: @router.post("/")
# 3. Validates request body against PaperCreate schema
# 4. If valid, calls create_paper() function
# 5. Function returns Paper object
# 6. FastAPI converts to JSON using PaperResponse schema
# 7. Sends JSON response to client
#
# All validation, serialization, and error handling is automatic!
