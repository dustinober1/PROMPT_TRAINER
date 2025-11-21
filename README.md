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

**Scoring Types Supported:**
- `yes_no` - Binary yes/no evaluation
- `meets` - Meets/Does not meet expectations
- `numerical` - Numeric scores (0-10)

Visit `http://localhost:8000/docs` for interactive API testing!

---

**Last Updated**: 2025-11-21
**Phase**: Sprint 1 (Day 5-7 Complete)
**Next**: Frontend Setup (Day 8-10)
