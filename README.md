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

**Next: Sprint 1** (Database & API Foundation)

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

### Running the Application (Coming in Sprint 1)

Backend will run on: `http://localhost:8000`
Frontend will run on: `http://localhost:5173`

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

---

**Last Updated**: 2025-11-21
**Phase**: Sprint 0 (Complete)
**Next Sprint**: Database & API Foundation
