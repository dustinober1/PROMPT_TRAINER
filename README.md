# Prompt Trainer - MVP

AI-powered paper grading system that learns from user feedback.

## Overview

Prompt Trainer helps educators grade papers using AI, while continuously improving grading accuracy through user feedback and automated prompt optimization.

## Current Status

**Sprint 0: Complete** ✅
- Development environment set up
- Project structure created
- Core dependencies installed
- Git repository initialized

**Sprint 1 (Days 1-4): Complete** ✅
- Database schema designed (6 tables)
- SQLAlchemy models created
- FastAPI application running
- Paper API with full CRUD operations
- Pydantic schemas for validation
- Interactive API docs at /docs

**Sprint 1 (Days 5-7): Complete** ✅
- Rubric API with nested criteria
- Support for 3 scoring types (yes_no, meets, numerical)
- Criterion management endpoints
- Comprehensive validation rules
- Full CRUD for rubrics and criteria
- 12 total API endpoints working

**Next: Sprint 1 (Days 8-10)** - Frontend setup with React

## Adapter / Model Provider Configuration

- Defaults to stub adapter (no external calls).
- To enable Ollama, set in `.env`:
  ```
  OLLAMA_ENABLED=true
  OLLAMA_BASE_URL=http://localhost:11434
  OLLAMA_MODEL=llama3.1:8b
  ```
- Health endpoint reports the active adapter; frontend status bar shows the adapter value.

## Prerequisites

- Python 3.11+ ✅ (You have 3.13.5)
- Node.js 18+ ✅ (You have v25.2.1)
- Ollama ✅ (Installed with qwen2.5:0.5b model)
- Git ✅

## Setup Instructions

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Verify dependencies are installed:
   ```bash
   pip list
   ```

4. Check configuration:
   ```bash
   cat .env
   ```

### Ollama Setup

1. Ensure Ollama is running:
   ```bash
   ollama list
   ```

2. You should see `qwen2.5:0.5b` in the list

### Running the Application

**Start the Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`

**Frontend** (Coming in Sprint 2):
- Will run on: `http://localhost:5173`

## Project Structure

```
Prompt_Trainer/
├── backend/
│   ├── app/
│   │   ├── api/          # API route handlers
│   │   ├── core/         # Core configurations
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── tests/        # Test files
│   ├── venv/             # Virtual environment
│   ├── .env              # Environment variables
│   ├── requirements.txt  # Python dependencies
│   └── pytest.ini        # Test configuration
├── frontend/             # React application (Sprint 1)
├── docs/                 # Project documentation
│   ├── backlog.md
│   ├── project-plan.md
│   └── mvp-development-plan.md
├── .gitignore
└── README.md
```

## Development

### Running Tests

```bash
cd backend
source venv/bin/activate
pytest
```

### Code Style

- Backend: Python with type hints
- Testing: pytest
- Database: SQLAlchemy ORM

## Next Steps

See `docs/mvp-development-plan.md` for detailed Sprint 1 tasks:
- Database schema design
- FastAPI application setup
- Basic CRUD endpoints
- React frontend initialization

## Documentation

- [Product Backlog](docs/backlog.md) - All features and user stories
- [Project Plan](docs/project-plan.md) - Strategic roadmap
- [MVP Development Plan](docs/mvp-development-plan.md) - Detailed sprint guide

## Questions?

Refer to the MVP Development Plan for:
- Tech explanations (Tech Tips throughout)
- Troubleshooting guide
- Architecture decisions

## API Endpoints (Available Now)

### Papers API
- `POST /api/papers/` - Create a new paper
- `GET /api/papers/` - List all papers (with pagination)
- `GET /api/papers/{id}` - Get a specific paper
- `PUT /api/papers/{id}` - Update a paper
- `DELETE /api/papers/{id}` - Delete a paper

### Rubrics API (NEW!)
- `POST /api/rubrics/` - Create rubric with criteria (nested)
- `GET /api/rubrics/` - List all rubrics
- `GET /api/rubrics/{id}` - Get rubric with all criteria
- `PUT /api/rubrics/{id}` - Update rubric metadata
- `DELETE /api/rubrics/{id}` - Delete rubric and criteria
- `PUT /api/rubrics/{id}/criteria/{criterion_id}` - Update criterion
- `DELETE /api/rubrics/{id}/criteria/{criterion_id}` - Delete criterion

Visit `http://localhost:8000/docs` for interactive API testing!

## Rubric Scoring Types

Prompt Trainer supports three different scoring methodologies to match various grading needs:

### 1. Yes/No (`yes_no`)
**Use When**: You need simple binary evaluation.

**Example Criteria**:
- "Has a clear thesis statement"
- "Includes at least 3 sources"
- "Uses proper APA citation format"

**How It Works**:
- Model responds with "yes" or "no" for each criterion
- Best for checklist-style evaluations
- Simple and fast to review

**Example Rubric**:
```json
{
  "name": "Essay Checklist",
  "scoring_type": "yes_no",
  "criteria": [
    {
      "name": "Has thesis",
      "description": "Paper includes a clear, arguable thesis statement",
      "order": 0
    }
  ]
}
```

### 2. Meets/Does Not Meet (`meets_not_meets`)
**Use When**: Grading against educational standards or competency requirements.

**Example Criteria**:
- "Meets Common Core Writing Standard W.1"
- "Demonstrates proficiency in statistical analysis"
- "Fulfills lab safety requirements"

**How It Works**:
- Model responds with "meets" or "does_not_meet"
- Ideal for standards-based grading
- Aligns with competency-based education

**Example Rubric**:
```json
{
  "name": "Common Core Standards",
  "scoring_type": "meets_not_meets",
  "criteria": [
    {
      "name": "Writing Standard W.1",
      "description": "Write arguments to support claims with clear reasons and relevant evidence",
      "order": 0
    }
  ]
}
```

### 3. Numerical (`numerical`)
**Use When**: You need weighted scoring or point-based grading.

**Example Criteria**:
- "Thesis clarity: 0-5 points"
- "Evidence quality: 0-10 points"
- "Writing style: 0-100 points"

**How It Works**:
- Each criterion specifies a min and max score (e.g., 0-10)
- Model returns a numerical score within that range
- Useful for complex rubrics with different weights
- **Required fields**: `min_score` and `max_score` for each criterion

**Example Rubric**:
```json
{
  "name": "Essay Grading Rubric",
  "scoring_type": "numerical",
  "criteria": [
    {
      "name": "Thesis Clarity",
      "description": "Clear, specific, and arguable thesis statement",
      "min_score": 0,
      "max_score": 5,
      "order": 0
    },
    {
      "name": "Evidence Quality",
      "description": "Strong peer-reviewed sources, properly cited",
      "min_score": 0,
      "max_score": 10,
      "order": 1
    }
  ]
}
```

### Tips for Writing Good Criterion Descriptions

**Do**:
- ✅ Be specific: "Includes at least 3 peer-reviewed sources published in the last 5 years"
- ✅ Provide measurable criteria: "Thesis statement appears in the first paragraph and makes a clear argument"
- ✅ Include context: "For a score of 8-10, paper must demonstrate exceptional understanding..."

**Don't**:
- ❌ Be vague: "Has good evidence"
- ❌ Use subjective terms without definition: "Well-written"
- ❌ Forget to explain scoring levels (for numerical rubrics)

**Description Limits**:
- Maximum 2000 characters per criterion description
- Supports plain text only (no HTML/script tags)

---

**Last Updated**: 2025-11-21
**Phase**: Sprint 1 (Day 5-7 Complete)
**Next**: Frontend Setup (Day 8-10)
