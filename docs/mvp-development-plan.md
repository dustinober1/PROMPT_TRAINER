# MVP Development Plan - Phase 1

## Table of Contents
- [Phase 1 Overview](#phase-1-overview)
- [Sprint 0: Pre-Development Setup](#sprint-0-pre-development-setup)
- [Sprint 1: Foundation (Weeks 1-2)](#sprint-1-foundation-weeks-1-2)
- [Sprint 2: Basic Grading (Weeks 3-4)](#sprint-2-basic-grading-weeks-3-4)
- [Sprint 3: Model Integration (Weeks 5-6)](#sprint-3-model-integration-weeks-5-6)
- [Sprint 4: Results & Feedback (Weeks 7-8)](#sprint-4-results--feedback-weeks-7-8)
- [Sprint 5: Prompts & Polish (Weeks 9-10)](#sprint-5-prompts--polish-weeks-9-10)
- [Testing & Validation Strategy](#testing--validation-strategy)
- [Technical Deep Dives](#technical-deep-dives)
- [Troubleshooting Guide](#troubleshooting-guide)
- [MVP Success Checklist](#mvp-success-checklist)

---

## Phase 1 Overview

### Objectives
Build a working prototype that proves the core concept: **an AI grading system that learns from user feedback**.

### What You'll Build
By the end of Phase 1, you'll have:
- ✅ A web application where users can submit papers
- ✅ A rubric builder for creating simple grading criteria
- ✅ Integration with Ollama (local AI models) for automated grading
- ✅ A feedback system where users can correct AI mistakes
- ✅ Manual prompt editing and version tracking
- ✅ Basic accuracy metrics

### What You WON'T Build (Yet)
- ❌ Automatic prompt improvement (Phase 2)
- ❌ API integrations (OpenAI/Claude) - Phase 2
- ❌ Advanced scoring types - Phase 2
- ❌ Multi-user support - Phase 3
- ❌ PDF/DOCX upload - Phase 3

### Success Criteria
- [ ] 5 beta users can successfully grade 100+ papers
- [ ] System achieves 60%+ accuracy rate
- [ ] Feedback loop works end-to-end
- [ ] Users can see improvement when they manually update prompts
- [ ] System is stable with no critical bugs

### Technology Stack (MVP)
```
Frontend:  React + TypeScript + Tailwind CSS
Backend:   FastAPI (Python)
Database:  SQLite (easy setup, no server needed)
AI Model:  Ollama (local, free)
Testing:   pytest (backend), Jest (frontend)
```

**Tech Tip**: We're using SQLite for MVP because it's just a file - no database server to install or configure. Later you'll migrate to PostgreSQL for multi-user support, but SQLite is perfect for learning and prototyping.

---

## Sprint 0: Pre-Development Setup

**Duration**: 2-3 days (before Sprint 1)
**Goal**: Get your development environment ready

### Checklist

#### 1. Install Required Software

**Python 3.11+**
```bash
# Check if you have Python
python --version

# If not, install from python.org or use Homebrew (Mac)
brew install python@3.11
```

**Node.js 18+** (for frontend)
```bash
# Check if you have Node
node --version

# Install using Homebrew (Mac)
brew install node
```

**Ollama** (local AI models)
```bash
# Mac
brew install ollama

# Start Ollama service
ollama serve

# In another terminal, pull a test model
ollama pull qwen2.5:0.5b
```

**Tech Tip**: Ollama runs as a background service and provides a REST API at `http://localhost:11434`. Your application will send requests to this endpoint to get AI responses.

**Git** (version control)
```bash
git --version
# Should be pre-installed on Mac
```

**VS Code** (or your preferred IDE)
- Download from code.visualstudio.com
- Install extensions:
  - Python
  - Pylance
  - ESLint
  - Prettier
  - Tailwind CSS IntelliSense

#### 2. Create Project Structure

```bash
cd /Users/dustinober/Projects/Prompt_Trainer

# Create main directories
mkdir -p backend frontend

# Backend structure
cd backend
mkdir -p app/{api,core,models,schemas,services,tests}
touch app/__init__.py
touch app/main.py

# Frontend structure
cd ../frontend
# We'll use Vite to create this in Sprint 1
```

**Tech Tip**: The `__init__.py` files make Python treat directories as packages, allowing you to import code between files.

#### 3. Initialize Git Repository

```bash
cd /Users/dustinober/Projects/Prompt_Trainer
git init
echo "node_modules/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
echo "*.db" >> .gitignore
echo ".DS_Store" >> .gitignore
git add .
git commit -m "Initial project structure"
```

#### 4. Set Up Python Virtual Environment

```bash
cd backend
python -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# Install core dependencies
pip install fastapi uvicorn sqlalchemy alembic pydantic python-dotenv httpx pytest
pip freeze > requirements.txt
```

**Tech Tip**: A virtual environment isolates your project's dependencies from your system Python. This prevents version conflicts between projects. Always activate it before working on the backend.

#### 5. Create Initial Configuration Files

**backend/.env** (environment variables)
```env
DATABASE_URL=sqlite:///./prompt_trainer.db
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=qwen2.5:0.5b
LOG_LEVEL=INFO
```

**backend/pyproject.toml** (optional, for better dependency management)
```toml
[tool.pytest.ini_options]
testpaths = ["app/tests"]
python_files = "test_*.py"
```

### Sprint 0 Deliverables
- [ ] All software installed and verified
- [ ] Project structure created
- [ ] Git initialized with first commit
- [ ] Python environment set up with dependencies
- [ ] Ollama running with test model downloaded

**Verification**: Run `ollama list` - you should see qwen2.5:0.5b listed.

---

## Sprint 1: Foundation (Weeks 1-2)

**Goal**: Set up database, API structure, and basic CRUD operations
**Backlog Items**: SD-001, PE-002, RM-003, UI-001

### Day 1-2: Database Schema Design

#### Task 1.1: Design Database Models

Create **backend/app/models/database.py**:

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    submission_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    evaluations = relationship("Evaluation", back_populates="paper")

class Rubric(Base):
    __tablename__ = "rubrics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    scoring_type = Column(String(50), default="yes_no")  # yes_no, meets, numerical
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    criteria = relationship("Criterion", back_populates="rubric", cascade="all, delete-orphan")
    evaluations = relationship("Evaluation", back_populates="rubric")

class Criterion(Base):
    __tablename__ = "criteria"

    id = Column(Integer, primary_key=True, index=True)
    rubric_id = Column(Integer, ForeignKey("rubrics.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, default=0)  # For display ordering

    # Relationships
    rubric = relationship("Rubric", back_populates="criteria")

class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(Integer, nullable=False)
    template_text = Column(Text, nullable=False)
    parent_version_id = Column(Integer, ForeignKey("prompts.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Performance metrics (calculated periodically)
    accuracy_rate = Column(Float, nullable=True)
    total_evaluations = Column(Integer, default=0)

    # Relationships
    evaluations = relationship("Evaluation", back_populates="prompt")

class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"))
    rubric_id = Column(Integer, ForeignKey("rubrics.id", ondelete="CASCADE"))
    prompt_id = Column(Integer, ForeignKey("prompts.id"))

    # Model's response (stored as JSON string for flexibility)
    model_response = Column(Text, nullable=False)  # JSON: {criterion_id: score, ...}

    # User feedback
    is_correct = Column(Boolean, nullable=True)  # null = not reviewed yet

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    paper = relationship("Paper", back_populates="evaluations")
    rubric = relationship("Rubric", back_populates="evaluations")
    prompt = relationship("Prompt", back_populates="evaluations")
    feedback_entries = relationship("FeedbackEntry", back_populates="evaluation", cascade="all, delete-orphan")

class FeedbackEntry(Base):
    __tablename__ = "feedback_entries"

    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id", ondelete="CASCADE"))
    criterion_id = Column(Integer, ForeignKey("criteria.id"))

    model_score = Column(String(50))  # What the model said
    user_corrected_score = Column(String(50))  # What user says is correct
    user_explanation = Column(Text, nullable=True)  # Why user corrected it

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    evaluation = relationship("Evaluation", back_populates="feedback_entries")
```

**Tech Tip**:
- **ORM (Object-Relational Mapping)**: SQLAlchemy lets you work with database tables as Python objects. Instead of writing SQL, you work with classes.
- **Relationships**: `relationship()` tells SQLAlchemy how tables connect. `back_populates` creates two-way references.
- **CASCADE**: When you delete a rubric, all its criteria are automatically deleted too.
- **ForeignKey**: Links rows between tables (e.g., each Evaluation belongs to one Paper).

#### Task 1.2: Database Connection Setup

Create **backend/app/core/database.py**:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Base
import os
from dotenv import load_env

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./prompt_trainer.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
def init_db():
    Base.metadata.create_all(bind=engine)
```

**Tech Tip**:
- **Session**: A session is like a "workspace" for database operations. You query data, make changes, then commit or rollback.
- **Dependency Injection**: `get_db()` is a "dependency" that FastAPI will call automatically to provide a database session to your routes.

### Day 3-4: API Structure & First Endpoints

#### Task 1.3: FastAPI Application Setup

Create **backend/app/main.py**:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import init_db
from app.api import papers, rubrics, evaluations, prompts

# Initialize FastAPI app
app = FastAPI(
    title="Prompt Trainer API",
    description="API for AI-powered paper grading with feedback loop",
    version="0.1.0"
)

# CORS - allows frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("✅ Database initialized")

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Prompt Trainer API",
        "status": "running",
        "version": "0.1.0"
    }

# Include routers (we'll create these next)
app.include_router(papers.router, prefix="/api/papers", tags=["papers"])
app.include_router(rubrics.router, prefix="/api/rubrics", tags=["rubrics"])
app.include_router(evaluations.router, prefix="/api/evaluations", tags=["evaluations"])
app.include_router(prompts.router, prefix="/api/prompts", tags=["prompts"])
```

**Tech Tip**:
- **CORS**: Cross-Origin Resource Sharing. Your frontend (port 5173) needs permission to call your backend (port 8000). Without CORS, browsers block the requests.
- **Routers**: Organize related endpoints together. All paper-related endpoints go in the papers router.
- **Tags**: Used in auto-generated API docs for organization.

#### Task 1.4: Create Pydantic Schemas

Create **backend/app/schemas/paper.py**:

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Schema for creating a paper (request)
class PaperCreate(BaseModel):
    title: str
    content: str

# Schema for paper response
class PaperResponse(BaseModel):
    id: int
    title: str
    content: str
    submission_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy models

# Schema for listing papers (less detail)
class PaperList(BaseModel):
    id: int
    title: str
    submission_date: datetime
    content_preview: str  # First 100 chars

    class Config:
        from_attributes = True
```

**Tech Tip**: Pydantic schemas define the shape of your API requests and responses. They:
- Validate incoming data (e.g., title must be a string)
- Auto-generate API documentation
- Serialize database models to JSON
- Provide type hints for better IDE support

Create similar schemas for rubrics, criteria, etc. (I'll show you the pattern)

#### Task 1.5: Create First API Endpoints

Create **backend/app/api/papers.py**:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.database import Paper
from app.schemas.paper import PaperCreate, PaperResponse, PaperList

router = APIRouter()

@router.post("/", response_model=PaperResponse, status_code=201)
async def create_paper(
    paper: PaperCreate,
    db: Session = Depends(get_db)
):
    """Create a new paper submission"""
    db_paper = Paper(
        title=paper.title,
        content=paper.content
    )
    db.add(db_paper)
    db.commit()
    db.refresh(db_paper)  # Get the ID that was auto-generated
    return db_paper

@router.get("/", response_model=List[PaperList])
async def list_papers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all papers"""
    papers = db.query(Paper).offset(skip).limit(limit).all()

    # Add content preview
    result = []
    for paper in papers:
        paper_dict = {
            "id": paper.id,
            "title": paper.title,
            "submission_date": paper.submission_date,
            "content_preview": paper.content[:100] + "..." if len(paper.content) > 100 else paper.content
        }
        result.append(PaperList(**paper_dict))

    return result

@router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper(
    paper_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific paper by ID"""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper

@router.delete("/{paper_id}", status_code=204)
async def delete_paper(
    paper_id: int,
    db: Session = Depends(get_db)
):
    """Delete a paper"""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    db.delete(paper)
    db.commit()
    return None
```

**Tech Tip**:
- **@router.post("/")**: This creates an endpoint at POST /api/papers/
- **Depends(get_db)**: FastAPI automatically calls get_db() and passes the session
- **response_model**: Tells FastAPI what schema to use for the response
- **status_code=201**: HTTP status code (201 = Created, 200 = OK, 404 = Not Found)

### Day 5-7: Frontend Setup

#### Task 1.6: Initialize React Project

```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

Configure **frontend/tailwind.config.js**:
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

Update **frontend/src/index.css**:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**Tech Tip**:
- **Vite**: A fast build tool for modern web projects. Much faster than Create React App.
- **TypeScript**: Adds type checking to JavaScript. Catches bugs before runtime.
- **Tailwind**: Utility-first CSS framework. Instead of writing CSS files, you add classes like `bg-blue-500 text-white p-4`.

#### Task 1.7: Install Additional Frontend Dependencies

```bash
npm install react-router-dom axios @tanstack/react-query
npm install -D @types/node
```

**Tech Tip**:
- **react-router-dom**: For navigation (different pages/URLs)
- **axios**: For making HTTP requests to your API
- **@tanstack/react-query**: Manages server state (caching, refetching, etc.)

#### Task 1.8: Create Basic Layout and Navigation

Create **frontend/src/components/Layout.tsx**:

```typescript
import { Link, Outlet } from 'react-router-dom';

export default function Layout() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-xl font-bold text-gray-900">
                  Prompt Trainer
                </h1>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <Link
                  to="/"
                  className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                >
                  Dashboard
                </Link>
                <Link
                  to="/papers"
                  className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                >
                  Papers
                </Link>
                <Link
                  to="/rubrics"
                  className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                >
                  Rubrics
                </Link>
                <Link
                  to="/prompts"
                  className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                >
                  Prompts
                </Link>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  );
}
```

**Tech Tip**:
- **<Outlet />**: This is where child routes render. Think of it as a placeholder for page content.
- **Tailwind classes**: `max-w-7xl` limits width, `mx-auto` centers it, `px-4` adds padding.

### Day 8-10: Testing & Documentation

#### Task 1.9: Write Backend Tests

Create **backend/app/tests/test_papers.py**:

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables after test
    Base.metadata.drop_all(bind=engine)

def test_create_paper():
    response = client.post(
        "/api/papers/",
        json={
            "title": "Test Paper",
            "content": "This is a test paper content."
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Paper"
    assert "id" in data

def test_list_papers():
    # Create a paper first
    client.post(
        "/api/papers/",
        json={"title": "Paper 1", "content": "Content 1"}
    )

    # List papers
    response = client.get("/api/papers/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Paper 1"

def test_get_paper_not_found():
    response = client.get("/api/papers/999")
    assert response.status_code == 404
```

Run tests:
```bash
cd backend
pytest
```

**Tech Tip**: Tests are your safety net. When you make changes later, tests ensure you didn't break existing functionality.

### Sprint 1 Deliverables
- [ ] Database schema designed and created
- [ ] FastAPI application running
- [ ] Paper CRUD endpoints working
- [ ] React frontend with navigation
- [ ] Basic tests passing
- [ ] API documentation accessible at http://localhost:8000/docs

**Verification Steps**:
1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Visit http://localhost:8000/docs - should see API documentation
3. Start frontend: `cd frontend && npm run dev`
4. Visit http://localhost:5173 - should see navigation
5. Run tests: `cd backend && pytest` - all should pass

---

## Sprint 2: Basic Grading (Weeks 3-4)

**Goal**: Build rubric creator and paper submission interface
**Backlog Items**: RM-001, RM-002, PE-001, RM-004

### Week 3: Rubric Builder

#### Task 2.1: Create Rubric API Endpoints

Create **backend/app/schemas/rubric.py**:

```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CriterionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    order: int = 0

class CriterionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    order: int

    class Config:
        from_attributes = True

class RubricCreate(BaseModel):
    name: str
    description: Optional[str] = None
    scoring_type: str = "yes_no"  # yes_no, meets, numerical
    criteria: List[CriterionCreate]

class RubricResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    scoring_type: str
    created_at: datetime
    criteria: List[CriterionResponse]

    class Config:
        from_attributes = True
```

Create **backend/app/api/rubrics.py**:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.database import Rubric, Criterion
from app.schemas.rubric import RubricCreate, RubricResponse

router = APIRouter()

@router.post("/", response_model=RubricResponse, status_code=201)
async def create_rubric(
    rubric: RubricCreate,
    db: Session = Depends(get_db)
):
    """Create a new rubric with criteria"""
    # Create rubric
    db_rubric = Rubric(
        name=rubric.name,
        description=rubric.description,
        scoring_type=rubric.scoring_type
    )
    db.add(db_rubric)
    db.flush()  # Get the ID without committing yet

    # Create criteria
    for criterion in rubric.criteria:
        db_criterion = Criterion(
            rubric_id=db_rubric.id,
            name=criterion.name,
            description=criterion.description,
            order=criterion.order
        )
        db.add(db_criterion)

    db.commit()
    db.refresh(db_rubric)
    return db_rubric

@router.get("/", response_model=List[RubricResponse])
async def list_rubrics(
    db: Session = Depends(get_db)
):
    """List all rubrics"""
    rubrics = db.query(Rubric).all()
    return rubrics

@router.get("/{rubric_id}", response_model=RubricResponse)
async def get_rubric(
    rubric_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific rubric"""
    rubric = db.query(Rubric).filter(Rubric.id == rubric_id).first()
    if not rubric:
        raise HTTPException(status_code=404, detail="Rubric not found")
    return rubric
```

**Tech Tip**:
- **db.flush()**: Writes to database but doesn't commit. This lets us get the rubric ID to use for criteria, but if something fails, everything rolls back.
- **Nested creates**: Creating a rubric with its criteria in one request is more user-friendly than separate requests.

#### Task 2.2: Build Rubric Builder UI with v0.dev

**Prompt for v0.dev**:
```
Create a React TypeScript component for building a grading rubric.

Requirements:
- Form with rubric name (text input) and description (textarea)
- Radio buttons for scoring type: "Yes/No", "Meets/Does Not Meet", "Numerical (0-10)"
- Dynamic list of criteria with add/remove buttons
- Each criterion has: name (text input), description (textarea), and drag handle for reordering
- "Create Rubric" button that validates and submits
- Use Tailwind CSS for styling
- Clean, professional design suitable for educators

The component should export a TypeScript interface for the rubric data.
```

Copy the generated component and save as **frontend/src/components/RubricBuilder.tsx**.

Then create the page that uses it:

**frontend/src/pages/Rubrics.tsx**:

```typescript
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import RubricBuilder from '../components/RubricBuilder';

const API_BASE = 'http://localhost:8000';

interface Rubric {
  id: number;
  name: string;
  description: string;
  scoring_type: string;
  created_at: string;
  criteria: Array<{
    id: number;
    name: string;
    description: string;
    order: number;
  }>;
}

export default function Rubrics() {
  const [showBuilder, setShowBuilder] = useState(false);
  const queryClient = useQueryClient();

  // Fetch rubrics
  const { data: rubrics, isLoading } = useQuery({
    queryKey: ['rubrics'],
    queryFn: async () => {
      const response = await axios.get<Rubric[]>(`${API_BASE}/api/rubrics/`);
      return response.data;
    }
  });

  // Create rubric mutation
  const createRubric = useMutation({
    mutationFn: async (rubric: any) => {
      const response = await axios.post(`${API_BASE}/api/rubrics/`, rubric);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rubrics'] });
      setShowBuilder(false);
    }
  });

  if (isLoading) return <div>Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Rubrics</h1>
        <button
          onClick={() => setShowBuilder(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Create Rubric
        </button>
      </div>

      {showBuilder && (
        <div className="bg-white p-6 rounded-lg shadow">
          <RubricBuilder
            onSubmit={(data) => createRubric.mutate(data)}
            onCancel={() => setShowBuilder(false)}
          />
        </div>
      )}

      {/* List existing rubrics */}
      <div className="grid gap-4">
        {rubrics?.map((rubric) => (
          <div key={rubric.id} className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold">{rubric.name}</h3>
            <p className="text-gray-600 text-sm mt-1">{rubric.description}</p>
            <div className="mt-4">
              <span className="text-sm font-medium text-gray-700">Criteria:</span>
              <ul className="mt-2 space-y-1">
                {rubric.criteria.map((criterion) => (
                  <li key={criterion.id} className="text-sm text-gray-600">
                    • {criterion.name}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

**Tech Tip**:
- **React Query**: Automatically handles loading states, caching, and refetching
- **Mutation**: A mutation is an operation that changes data (create, update, delete)
- **invalidateQueries**: After creating a rubric, this refetches the list so you see the new one

### Week 4: Paper Submission Interface

#### Task 2.3: Create Paper Submission Form

Use v0.dev prompt:
```
Create a React TypeScript component for submitting a paper for grading.

Requirements:
- Form with fields: title (text), content (large textarea)
- Dropdown to select a rubric from a list
- Character count for the paper content
- "Submit for Grading" button
- Clean, spacious design with proper validation
- Use Tailwind CSS
- Show loading state while submitting

Export TypeScript interface for the form data.
```

Save as **frontend/src/components/PaperSubmissionForm.tsx**.

#### Task 2.4: Create Papers Page

**frontend/src/pages/Papers.tsx**:

```typescript
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import PaperSubmissionForm from '../components/PaperSubmissionForm';
import { Link } from 'react-router-dom';

const API_BASE = 'http://localhost:8000';

export default function Papers() {
  const [showForm, setShowForm] = useState(false);
  const queryClient = useQueryClient();

  const { data: papers } = useQuery({
    queryKey: ['papers'],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE}/api/papers/`);
      return response.data;
    }
  });

  const submitPaper = useMutation({
    mutationFn: async (paper: any) => {
      const response = await axios.post(`${API_BASE}/api/papers/`, paper);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['papers'] });
      setShowForm(false);
    }
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Papers</h1>
        <button
          onClick={() => setShowForm(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Submit Paper
        </button>
      </div>

      {showForm && (
        <PaperSubmissionForm
          onSubmit={(data) => submitPaper.mutate(data)}
          onCancel={() => setShowForm(false)}
        />
      )}

      {/* List papers */}
      <div className="grid gap-4">
        {papers?.map((paper: any) => (
          <Link
            key={paper.id}
            to={`/papers/${paper.id}`}
            className="bg-white p-6 rounded-lg shadow hover:shadow-md transition"
          >
            <h3 className="text-lg font-semibold">{paper.title}</h3>
            <p className="text-gray-600 text-sm mt-2">{paper.content_preview}</p>
            <p className="text-gray-400 text-xs mt-2">
              Submitted: {new Date(paper.submission_date).toLocaleDateString()}
            </p>
          </Link>
        ))}
      </div>
    </div>
  );
}
```

### Sprint 2 Deliverables
- [ ] Rubric builder UI working
- [ ] Can create rubrics with multiple criteria
- [ ] Paper submission form working
- [ ] Can submit papers and see them in list
- [ ] Papers can be associated with rubrics
- [ ] Basic validation in place

---

## Sprint 3: Model Integration (Weeks 5-6)

**Goal**: Connect to Ollama and generate first AI evaluations
**Backlog Items**: MI-001, MI-002, PE-003, MI-003

### Week 5: Ollama Integration

#### Task 3.1: Create Model Abstraction Layer

**backend/app/services/model_provider.py**:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any
import httpx
import json
import os

class ModelProvider(ABC):
    """Abstract base class for model providers"""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if model service is available"""
        pass

class OllamaProvider(ModelProvider):
    """Ollama local model provider"""

    def __init__(self, base_url: str = None, model_name: str = None):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model_name = model_name or os.getenv("DEFAULT_MODEL", "qwen2.5:0.5b")

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from Ollama"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": kwargs.get("temperature", 0.0),
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
            except Exception as e:
                raise Exception(f"Ollama generation failed: {str(e)}")

    async def health_check(self) -> bool:
        """Check if Ollama is running"""
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
            except:
                return False

# Factory function
def get_model_provider(provider_type: str = "ollama") -> ModelProvider:
    """Get model provider instance"""
    if provider_type == "ollama":
        return OllamaProvider()
    # Future: add OpenAI, Anthropic, etc.
    raise ValueError(f"Unknown provider type: {provider_type}")
```

**Tech Tip**:
- **Abstract Base Class (ABC)**: Defines an interface. All providers must implement `generate()` and `health_check()`.
- **Factory Pattern**: `get_model_provider()` returns the right provider based on type. Makes it easy to add new providers later.
- **async/await**: Asynchronous programming. The server can handle other requests while waiting for Ollama to respond.

#### Task 3.2: Create Prompt Template System

**backend/app/services/prompt_builder.py**:

```python
from typing import Dict, List
from app.models.database import Paper, Rubric, Criterion

class PromptBuilder:
    """Builds prompts for paper evaluation"""

    @staticmethod
    def build_evaluation_prompt(
        paper: Paper,
        rubric: Rubric,
        prompt_template: str = None
    ) -> str:
        """Build prompt for evaluating a paper"""

        # Default template if none provided
        if not prompt_template:
            prompt_template = PromptBuilder.get_default_template()

        # Build criteria description
        criteria_text = "\n".join([
            f"{i+1}. {criterion.name}: {criterion.description or 'Evaluate this criterion.'}"
            for i, criterion in enumerate(rubric.criteria)
        ])

        # Determine scoring instructions based on rubric type
        if rubric.scoring_type == "yes_no":
            scoring_instructions = "For each criterion, respond with either 'yes' or 'no'."
        elif rubric.scoring_type == "meets":
            scoring_instructions = "For each criterion, respond with either 'meets' or 'does not meet'."
        else:  # numerical
            scoring_instructions = "For each criterion, provide a score from 0 to 10."

        # Fill in template
        prompt = prompt_template.format(
            paper_title=paper.title,
            paper_content=paper.content,
            rubric_name=rubric.name,
            criteria=criteria_text,
            scoring_instructions=scoring_instructions
        )

        return prompt

    @staticmethod
    def get_default_template() -> str:
        """Get default evaluation prompt template"""
        return """You are an expert paper grader. Evaluate the following paper using the provided rubric.

Paper Title: {paper_title}

Paper Content:
{paper_content}

Rubric: {rubric_name}

Criteria:
{criteria}

Scoring Instructions: {scoring_instructions}

Please evaluate this paper for each criterion. Provide your evaluation in the following JSON format:
{{
  "evaluations": [
    {{"criterion_number": 1, "score": "your_score", "reasoning": "brief explanation"}},
    {{"criterion_number": 2, "score": "your_score", "reasoning": "brief explanation"}}
  ]
}}

Ensure your response is valid JSON and includes all criteria."""

    @staticmethod
    def parse_evaluation_response(response: str) -> Dict:
        """Parse model's JSON response"""
        import json
        import re

        # Try to extract JSON from response (model might include extra text)
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                raise ValueError("Could not parse model response as JSON")
        else:
            raise ValueError("No JSON found in model response")
```

**Tech Tip**:
- **Template Pattern**: The prompt is a template with placeholders like `{paper_content}`. We fill them in with actual data.
- **JSON output**: We ask the model to respond in JSON format so we can easily parse its evaluation.
- **Regex**: `re.search()` finds JSON in the response even if the model adds extra text before/after.

#### Task 3.3: Create Evaluation Service

**backend/app/services/evaluation_service.py**:

```python
from sqlalchemy.orm import Session
from app.models.database import Paper, Rubric, Evaluation, Prompt
from app.services.model_provider import get_model_provider
from app.services.prompt_builder import PromptBuilder
import json

class EvaluationService:
    """Service for evaluating papers"""

    def __init__(self, db: Session):
        self.db = db
        self.model_provider = get_model_provider("ollama")
        self.prompt_builder = PromptBuilder()

    async def evaluate_paper(
        self,
        paper_id: int,
        rubric_id: int
    ) -> Evaluation:
        """Evaluate a paper using a rubric"""

        # Fetch paper and rubric
        paper = self.db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise ValueError(f"Paper {paper_id} not found")

        rubric = self.db.query(Rubric).filter(Rubric.id == rubric_id).first()
        if not rubric:
            raise ValueError(f"Rubric {rubric_id} not found")

        # Get active prompt
        active_prompt = self.db.query(Prompt).filter(
            Prompt.is_active == True
        ).order_by(Prompt.version.desc()).first()

        if not active_prompt:
            # Create default prompt if none exists
            active_prompt = Prompt(
                version=1,
                template_text=PromptBuilder.get_default_template(),
                is_active=True
            )
            self.db.add(active_prompt)
            self.db.commit()
            self.db.refresh(active_prompt)

        # Build prompt
        prompt_text = self.prompt_builder.build_evaluation_prompt(
            paper=paper,
            rubric=rubric,
            prompt_template=active_prompt.template_text
        )

        # Call model
        model_response = await self.model_provider.generate(prompt_text)

        # Parse response
        try:
            parsed_response = self.prompt_builder.parse_evaluation_response(model_response)
        except ValueError as e:
            # If parsing fails, store raw response
            parsed_response = {"error": str(e), "raw_response": model_response}

        # Create evaluation record
        evaluation = Evaluation(
            paper_id=paper_id,
            rubric_id=rubric_id,
            prompt_id=active_prompt.id,
            model_response=json.dumps(parsed_response)
        )
        self.db.add(evaluation)

        # Update prompt stats
        active_prompt.total_evaluations += 1

        self.db.commit()
        self.db.refresh(evaluation)

        return evaluation
```

**Tech Tip**:
- **Service Layer**: This separates business logic from API routes. Routes handle HTTP stuff, services handle core logic.
- **Error Handling**: If JSON parsing fails, we store the raw response so you can debug.
- **Stats Tracking**: We increment `total_evaluations` on the prompt for analytics later.

### Week 6: Evaluation API Endpoints

#### Task 3.4: Create Evaluation Endpoints

**backend/app/schemas/evaluation.py**:

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class EvaluationCreate(BaseModel):
    paper_id: int
    rubric_id: int

class EvaluationResponse(BaseModel):
    id: int
    paper_id: int
    rubric_id: int
    prompt_id: int
    model_response: str  # JSON string
    is_correct: Optional[bool]
    created_at: datetime

    class Config:
        from_attributes = True
```

**backend/app/api/evaluations.py**:

```python
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.evaluation import EvaluationCreate, EvaluationResponse
from app.services.evaluation_service import EvaluationService
import json

router = APIRouter()

@router.post("/", response_model=EvaluationResponse, status_code=201)
async def create_evaluation(
    evaluation_request: EvaluationCreate,
    db: Session = Depends(get_db)
):
    """Evaluate a paper using a rubric"""
    service = EvaluationService(db)

    try:
        evaluation = await service.evaluate_paper(
            paper_id=evaluation_request.paper_id,
            rubric_id=evaluation_request.rubric_id
        )
        return evaluation
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

@router.get("/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """Get an evaluation by ID"""
    from app.models.database import Evaluation
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return evaluation

@router.get("/paper/{paper_id}", response_model=list[EvaluationResponse])
async def get_paper_evaluations(
    paper_id: int,
    db: Session = Depends(get_db)
):
    """Get all evaluations for a paper"""
    from app.models.database import Evaluation
    evaluations = db.query(Evaluation).filter(Evaluation.paper_id == paper_id).all()
    return evaluations
```

#### Task 3.5: Create Evaluation Display UI

Use v0.dev:
```
Create a React TypeScript component to display paper evaluation results.

Requirements:
- Shows paper title and content in a card
- Displays rubric name
- Lists each criterion with:
  - Criterion name
  - Model's score (highlighted)
  - Model's reasoning
- Include a "Provide Feedback" button for each criterion
- Professional, readable design with Tailwind CSS
- Handle loading and error states

Export TypeScript interfaces for the data.
```

Save as **frontend/src/components/EvaluationDisplay.tsx**.

Create paper detail page:

**frontend/src/pages/PaperDetail.tsx**:

```typescript
import { useParams } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import axios from 'axios';
import { useState } from 'react';
import EvaluationDisplay from '../components/EvaluationDisplay';

const API_BASE = 'http://localhost:8000';

export default function PaperDetail() {
  const { paperId } = useParams();
  const [selectedRubricId, setSelectedRubricId] = useState<number | null>(null);

  const { data: paper } = useQuery({
    queryKey: ['paper', paperId],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE}/api/papers/${paperId}`);
      return response.data;
    }
  });

  const { data: rubrics } = useQuery({
    queryKey: ['rubrics'],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE}/api/rubrics/`);
      return response.data;
    }
  });

  const { data: evaluations } = useQuery({
    queryKey: ['evaluations', paperId],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE}/api/evaluations/paper/${paperId}`);
      return response.data;
    }
  });

  const evaluatePaper = useMutation({
    mutationFn: async (rubricId: number) => {
      const response = await axios.post(`${API_BASE}/api/evaluations/`, {
        paper_id: parseInt(paperId!),
        rubric_id: rubricId
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['evaluations', paperId] });
    }
  });

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <h1 className="text-2xl font-bold mb-4">{paper?.title}</h1>
        <div className="prose max-w-none">
          <p className="whitespace-pre-wrap">{paper?.content}</p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Grade this Paper</h2>
        <div className="flex gap-4">
          <select
            className="flex-1 border border-gray-300 rounded-md px-4 py-2"
            value={selectedRubricId || ''}
            onChange={(e) => setSelectedRubricId(parseInt(e.target.value))}
          >
            <option value="">Select a rubric...</option>
            {rubrics?.map((rubric: any) => (
              <option key={rubric.id} value={rubric.id}>
                {rubric.name}
              </option>
            ))}
          </select>
          <button
            onClick={() => selectedRubricId && evaluatePaper.mutate(selectedRubricId)}
            disabled={!selectedRubricId || evaluatePaper.isPending}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300"
          >
            {evaluatePaper.isPending ? 'Grading...' : 'Grade Paper'}
          </button>
        </div>
      </div>

      {evaluations?.map((evaluation: any) => (
        <EvaluationDisplay key={evaluation.id} evaluation={evaluation} />
      ))}
    </div>
  );
}
```

### Sprint 3 Deliverables
- [ ] Ollama integration working
- [ ] Model abstraction layer complete
- [ ] Can evaluate papers and see results
- [ ] Prompt template system functional
- [ ] Error handling for model failures
- [ ] Loading states in UI

**Verification**:
1. Ensure Ollama is running: `ollama list`
2. Submit a paper with a rubric
3. Click "Grade Paper"
4. Should see AI-generated evaluation within 10-30 seconds

---

## Sprint 4: Results & Feedback (Weeks 7-8)

**Goal**: Build feedback collection interface
**Backlog Items**: FC-001, FC-002, FC-003, FC-004, FC-005

### Week 7: Feedback System

#### Task 4.1: Create Feedback API

**backend/app/schemas/feedback.py**:

```python
from pydantic import BaseModel
from typing import Optional

class FeedbackCreate(BaseModel):
    evaluation_id: int
    criterion_id: int
    model_score: str
    user_corrected_score: str
    user_explanation: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: int
    evaluation_id: int
    criterion_id: int
    model_score: str
    user_corrected_score: str
    user_explanation: Optional[str]

    class Config:
        from_attributes = True
```

**backend/app/api/feedback.py**:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.database import FeedbackEntry, Evaluation
from app.schemas.feedback import FeedbackCreate, FeedbackResponse

router = APIRouter()

@router.post("/", response_model=FeedbackResponse, status_code=201)
async def create_feedback(
    feedback: FeedbackCreate,
    db: Session = Depends(get_db)
):
    """Submit feedback on an evaluation"""

    # Verify evaluation exists
    evaluation = db.query(Evaluation).filter(Evaluation.id == feedback.evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    # Create feedback
    db_feedback = FeedbackEntry(
        evaluation_id=feedback.evaluation_id,
        criterion_id=feedback.criterion_id,
        model_score=feedback.model_score,
        user_corrected_score=feedback.user_corrected_score,
        user_explanation=feedback.user_explanation
    )
    db.add(db_feedback)

    # Update evaluation's is_correct field
    # (If any criterion is corrected, evaluation is marked incorrect)
    evaluation.is_correct = False

    db.commit()
    db.refresh(db_feedback)

    return db_feedback

@router.get("/evaluation/{evaluation_id}", response_model=list[FeedbackResponse])
async def get_evaluation_feedback(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """Get all feedback for an evaluation"""
    feedback = db.query(FeedbackEntry).filter(
        FeedbackEntry.evaluation_id == evaluation_id
    ).all()
    return feedback
```

Add this router to main.py:
```python
from app.api import feedback
app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])
```

#### Task 4.2: Create Feedback UI Components

Use v0.dev:
```
Create a React TypeScript component for submitting feedback on a grading criterion.

Requirements:
- Display: criterion name, model's score
- Checkbox: "This evaluation is incorrect"
- When checked, show:
  - Dropdown or input for correct score
  - Textarea for explanation (optional)
  - "Submit Feedback" button
- When unchecked, show "Mark as Correct" button
- Clean, inline design that fits in evaluation display
- Use Tailwind CSS
- Handle loading and success states

Export TypeScript interfaces.
```

Save as **frontend/src/components/FeedbackForm.tsx**.

Update **EvaluationDisplay.tsx** to include FeedbackForm for each criterion.

### Week 8: Mark Evaluations Correct/Incorrect

#### Task 4.3: Create Endpoint to Mark Evaluation Correct

Update **backend/app/api/evaluations.py**:

```python
@router.patch("/{evaluation_id}/mark-correct", response_model=EvaluationResponse)
async def mark_evaluation_correct(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """Mark an evaluation as correct"""
    from app.models.database import Evaluation, Prompt

    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    evaluation.is_correct = True

    # Update prompt accuracy
    prompt = db.query(Prompt).filter(Prompt.id == evaluation.prompt_id).first()
    if prompt:
        # Recalculate accuracy
        total_evals = db.query(Evaluation).filter(
            Evaluation.prompt_id == prompt.id,
            Evaluation.is_correct.isnot(None)
        ).count()

        correct_evals = db.query(Evaluation).filter(
            Evaluation.prompt_id == prompt.id,
            Evaluation.is_correct == True
        ).count()

        if total_evals > 0:
            prompt.accuracy_rate = (correct_evals / total_evals) * 100

    db.commit()
    db.refresh(evaluation)

    return evaluation
```

**Tech Tip**: This endpoint calculates accuracy in real-time. Later, you might move this to a background job for better performance.

#### Task 4.4: Add Feedback Stats Dashboard

Create **backend/app/api/stats.py**:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.database import Evaluation, FeedbackEntry, Prompt, Paper

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get key metrics for dashboard"""

    # Total papers
    total_papers = db.query(func.count(Paper.id)).scalar()

    # Total evaluations
    total_evaluations = db.query(func.count(Evaluation.id)).scalar()

    # Accuracy rate (evaluations marked correct / total reviewed)
    reviewed_count = db.query(Evaluation).filter(
        Evaluation.is_correct.isnot(None)
    ).count()

    correct_count = db.query(Evaluation).filter(
        Evaluation.is_correct == True
    ).count()

    accuracy_rate = (correct_count / reviewed_count * 100) if reviewed_count > 0 else 0

    # Feedback collected
    total_feedback = db.query(func.count(FeedbackEntry.id)).scalar()

    # Active prompt version
    active_prompt = db.query(Prompt).filter(
        Prompt.is_active == True
    ).first()

    return {
        "total_papers": total_papers,
        "total_evaluations": total_evaluations,
        "accuracy_rate": round(accuracy_rate, 1),
        "feedback_collected": total_feedback,
        "current_prompt_version": active_prompt.version if active_prompt else 0,
        "reviewed_evaluations": reviewed_count
    }
```

Add to main.py:
```python
from app.api import stats
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
```

Create dashboard page:

**frontend/src/pages/Dashboard.tsx**:

```typescript
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export default function Dashboard() {
  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE}/api/stats/dashboard`);
      return response.data;
    },
    refetchInterval: 30000 // Refresh every 30 seconds
  });

  const metrics = [
    { label: 'Papers Graded', value: stats?.total_papers || 0 },
    { label: 'Total Evaluations', value: stats?.total_evaluations || 0 },
    { label: 'Accuracy Rate', value: `${stats?.accuracy_rate || 0}%` },
    { label: 'Feedback Collected', value: stats?.feedback_collected || 0 },
    { label: 'Prompt Version', value: `v${stats?.current_prompt_version || 0}` },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {metrics.map((metric) => (
          <div key={metric.label} className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-1">
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    {metric.label}
                  </dt>
                  <dd className="mt-1 text-3xl font-semibold text-gray-900">
                    {metric.value}
                  </dd>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Quick Stats</h2>
        <div className="space-y-2">
          <p className="text-sm text-gray-600">
            You've reviewed {stats?.reviewed_evaluations || 0} evaluations
          </p>
          <p className="text-sm text-gray-600">
            {stats?.feedback_collected || 0} corrections provided to improve prompts
          </p>
        </div>
      </div>
    </div>
  );
}
```

### Sprint 4 Deliverables
- [ ] Feedback submission working
- [ ] Can mark evaluations as correct/incorrect
- [ ] Can provide corrected scores and explanations
- [ ] Dashboard shows accuracy metrics
- [ ] Feedback stored in database
- [ ] UI updates in real-time

---

## Sprint 5: Prompts & Polish (Weeks 9-10)

**Goal**: Manual prompt management and MVP polish
**Backlog Items**: PI-001, PI-002, PI-003, AR-001, UI-002, SD-002

### Week 9: Prompt Management

#### Task 5.1: Create Prompt Management API

**backend/app/schemas/prompt.py**:

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PromptCreate(BaseModel):
    template_text: str
    parent_version_id: Optional[int] = None

class PromptUpdate(BaseModel):
    template_text: str

class PromptResponse(BaseModel):
    id: int
    version: int
    template_text: str
    parent_version_id: Optional[int]
    created_at: datetime
    is_active: bool
    accuracy_rate: Optional[float]
    total_evaluations: int

    class Config:
        from_attributes = True
```

**backend/app/api/prompts.py**:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.database import Prompt
from app.schemas.prompt import PromptCreate, PromptResponse
from typing import List

router = APIRouter()

@router.get("/", response_model=List[PromptResponse])
async def list_prompts(db: Session = Depends(get_db)):
    """List all prompt versions"""
    prompts = db.query(Prompt).order_by(Prompt.version.desc()).all()
    return prompts

@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(prompt_id: int, db: Session = Depends(get_db)):
    """Get a specific prompt"""
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt

@router.get("/active/current", response_model=PromptResponse)
async def get_active_prompt(db: Session = Depends(get_db)):
    """Get currently active prompt"""
    prompt = db.query(Prompt).filter(Prompt.is_active == True).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="No active prompt found")
    return prompt

@router.post("/", response_model=PromptResponse, status_code=201)
async def create_prompt(
    prompt_data: PromptCreate,
    db: Session = Depends(get_db)
):
    """Create a new prompt version"""

    # Get latest version number
    latest = db.query(Prompt).order_by(Prompt.version.desc()).first()
    new_version = (latest.version + 1) if latest else 1

    # Deactivate all other prompts
    db.query(Prompt).update({"is_active": False})

    # Create new prompt
    new_prompt = Prompt(
        version=new_version,
        template_text=prompt_data.template_text,
        parent_version_id=prompt_data.parent_version_id,
        is_active=True
    )
    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)

    return new_prompt

@router.patch("/{prompt_id}/activate", response_model=PromptResponse)
async def activate_prompt(
    prompt_id: int,
    db: Session = Depends(get_db)
):
    """Activate a specific prompt version"""
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    # Deactivate all prompts
    db.query(Prompt).update({"is_active": False})

    # Activate this one
    prompt.is_active = True
    db.commit()
    db.refresh(prompt)

    return prompt
```

#### Task 5.2: Build Prompt Editor UI

Use v0.dev:
```
Create a React TypeScript component for managing prompt versions.

Requirements:
- List of all prompt versions with:
  - Version number
  - Created date
  - Accuracy rate (if available)
  - Total evaluations
  - "Active" badge for current version
  - "Activate" button for inactive versions
- Click a version to expand and see full template text
- "Create New Version" button that opens a modal with:
  - Large textarea for template text
  - "Based on version X" dropdown
  - Save and Cancel buttons
- Code/monospace font for template text
- Professional design with Tailwind CSS

Export TypeScript interfaces.
```

Save as **frontend/src/components/PromptManager.tsx**.

Create prompts page:

**frontend/src/pages/Prompts.tsx**:

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import PromptManager from '../components/PromptManager';

const API_BASE = 'http://localhost:8000';

export default function Prompts() {
  const queryClient = useQueryClient();

  const { data: prompts } = useQuery({
    queryKey: ['prompts'],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE}/api/prompts/`);
      return response.data;
    }
  });

  const createPrompt = useMutation({
    mutationFn: async (data: any) => {
      const response = await axios.post(`${API_BASE}/api/prompts/`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompts'] });
    }
  });

  const activatePrompt = useMutation({
    mutationFn: async (promptId: number) => {
      const response = await axios.patch(`${API_BASE}/api/prompts/${promptId}/activate`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompts'] });
    }
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Prompt Management</h1>

      <PromptManager
        prompts={prompts || []}
        onCreatePrompt={createPrompt.mutate}
        onActivatePrompt={activatePrompt.mutate}
      />
    </div>
  );
}
```

### Week 10: Polish & Testing

#### Task 5.3: Add Input Validation

Update all Pydantic schemas with validation:

```python
from pydantic import BaseModel, Field, validator

class PaperCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=10)  # At least 10 characters

    @validator('title')
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v
```

Add frontend validation using React Hook Form.

#### Task 5.4: Error Handling & Loading States

Add error boundaries and consistent error handling across frontend.

Create **frontend/src/components/ErrorBoundary.tsx**:

```typescript
import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">
              Something went wrong
            </h1>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-blue-600 text-white rounded-md"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
```

#### Task 5.5: Comprehensive Testing

**Backend Tests**:

Add tests for all endpoints:

```bash
cd backend
pytest app/tests/ -v --cov=app
```

Target 70%+ code coverage.

**Frontend Tests**:

Add component tests:

```bash
cd frontend
npm test
```

#### Task 5.6: Documentation

Create **README.md** in project root:

```markdown
# Prompt Trainer - MVP

AI-powered paper grading system that learns from feedback.

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Ollama

### Installation

1. Install Ollama and pull model:
   ```bash
   brew install ollama
   ollama serve
   ollama pull qwen2.5:0.5b
   ```

2. Setup backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Setup frontend:
   ```bash
   cd frontend
   npm install
   ```

### Running

1. Start backend:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. Start frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Visit http://localhost:5173

## Usage

1. Create a rubric with grading criteria
2. Submit a paper
3. Select rubric and grade the paper
4. Review AI evaluation and provide feedback
5. Manually update prompts to improve accuracy

## Testing

Backend: `cd backend && pytest`
Frontend: `cd frontend && npm test`
```

### Sprint 5 Deliverables
- [ ] Prompt version management working
- [ ] Can create and activate prompt versions
- [ ] Input validation on all forms
- [ ] Error handling throughout app
- [ ] Tests written and passing
- [ ] Documentation complete
- [ ] **MVP READY FOR BETA TESTING**

---

## Testing & Validation Strategy

### Manual Testing Checklist

Before declaring MVP complete, test these scenarios:

#### Rubric Creation
- [ ] Create rubric with 1 criterion
- [ ] Create rubric with 5 criteria
- [ ] Try creating rubric with empty name (should fail)
- [ ] Delete rubric (should work if no evaluations)

#### Paper Submission
- [ ] Submit paper with < 10 characters (should fail)
- [ ] Submit valid paper
- [ ] View paper in list
- [ ] Delete paper

#### Evaluation
- [ ] Evaluate paper with yes/no rubric
- [ ] Verify model response appears
- [ ] Check that response is valid JSON
- [ ] Test with Ollama offline (should show error)

#### Feedback
- [ ] Mark evaluation as correct
- [ ] Mark criterion as incorrect and provide correction
- [ ] Add explanation
- [ ] Verify feedback saved
- [ ] Check accuracy updates

#### Prompts
- [ ] View default prompt
- [ ] Create new prompt version
- [ ] Activate different version
- [ ] Verify new evaluations use active prompt

#### Dashboard
- [ ] Verify metrics update after actions
- [ ] Check accuracy calculation
- [ ] Refresh page, metrics should persist

### Beta Testing Plan

**Week 11**: Beta Testing (5 Users)

1. **Recruit Testers**:
   - Ideal: Teachers or TAs who grade papers
   - Give them access and basic instructions

2. **Testing Tasks**:
   - Each tester grades 20 papers
   - Provide feedback on 10 evaluations
   - Update prompt once based on feedback
   - Complete feedback survey

3. **Feedback Collection**:
   - What worked well?
   - What was confusing?
   - Did accuracy improve after prompt update?
   - What features are missing?

4. **Success Metrics**:
   - [ ] All testers complete 20 papers
   - [ ] Average accuracy > 60%
   - [ ] Satisfaction score > 3.5/5
   - [ ] No critical bugs reported

---

## Technical Deep Dives

### Understanding Async/Await

```python
# Synchronous (blocking)
def grade_paper():
    response = requests.post(ollama_url)  # Waits here, blocks server
    return response

# Asynchronous (non-blocking)
async def grade_paper():
    response = await httpx.post(ollama_url)  # Server can handle other requests
    return response
```

**Why it matters**: When waiting for Ollama (10-30 seconds), the server can handle other users' requests instead of being blocked.

### Database Relationships Explained

```python
class Rubric(Base):
    criteria = relationship("Criterion", back_populates="rubric")

class Criterion(Base):
    rubric = relationship("Rubric", back_populates="criteria")
```

**Result**:
- `rubric.criteria` gives you all criteria for a rubric
- `criterion.rubric` gives you the parent rubric
- SQLAlchemy handles the SQL JOINs automatically

### React Query Explained

```typescript
const { data, isLoading } = useQuery({
  queryKey: ['papers'],
  queryFn: fetchPapers
});
```

**What it does**:
- Fetches data when component mounts
- Caches result (subsequent renders are instant)
- Refetches when you call `invalidateQueries`
- Provides loading states automatically

### Prompt Engineering Basics

**Good prompts are**:
- **Specific**: Clear instructions, not vague
- **Structured**: Use formatting, numbered lists
- **Example-driven**: Show examples of good output
- **Constrained**: Specify output format (JSON, specific values)

**Bad prompt**:
```
Grade this paper.
```

**Good prompt**:
```
You are an expert paper grader. Evaluate the following paper...

Respond in this JSON format:
{"criterion_1": "yes", "reasoning": "..."}
```

---

## Troubleshooting Guide

### Issue: "Connection refused" when calling Ollama

**Solution**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

### Issue: Database locked (SQLite)

**Solution**:
```python
# In database.py, increase timeout
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30}
)
```

### Issue: Frontend can't reach backend (CORS)

**Solution**: Verify CORS settings in `main.py` include your frontend URL:
```python
allow_origins=["http://localhost:5173"]
```

### Issue: Model responses aren't valid JSON

**Solution**:
- Check your prompt template is clear about JSON format
- Add examples of correct JSON in prompt
- Use `temperature=0` for more consistent output
- Try a better model (qwen2.5:3b instead of 0.5b)

### Issue: Tests failing with database errors

**Solution**:
```python
# Use separate test database
@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")  # In-memory DB
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
```

---

## MVP Success Checklist

### Technical Completeness
- [ ] All database tables created
- [ ] All API endpoints working
- [ ] Frontend routing complete
- [ ] Forms validated
- [ ] Error handling in place
- [ ] Tests passing

### Core Features
- [ ] Can create rubrics
- [ ] Can submit papers
- [ ] Can evaluate papers with Ollama
- [ ] Can view evaluation results
- [ ] Can provide feedback
- [ ] Can manage prompt versions
- [ ] Dashboard shows metrics

### Quality
- [ ] No critical bugs
- [ ] Loading states for all async operations
- [ ] Error messages are clear
- [ ] UI is responsive (mobile + desktop)
- [ ] Code is documented
- [ ] README has setup instructions

### Beta Ready
- [ ] 5 beta testers identified
- [ ] Feedback survey created
- [ ] Installation guide written
- [ ] Support plan in place
- [ ] Way to collect bug reports

---

## Next Steps After MVP

Once MVP is validated:

1. **Analyze Beta Feedback**
   - What accuracy did users achieve?
   - Which features were most valuable?
   - What was confusing?

2. **Plan Phase 2**
   - Prioritize automatic prompt improvement
   - Add API integrations (OpenAI/Claude)
   - Implement remaining scoring types

3. **Technical Debt**
   - Migrate to PostgreSQL if multi-user needed
   - Add caching layer (Redis)
   - Optimize slow queries
   - Improve test coverage

4. **Product Decisions**
   - Should you build desktop app or web app?
   - Freemium vs paid model?
   - Enterprise features needed?

---

*Last Updated: 2025-11-21*
*Version: 1.0*
