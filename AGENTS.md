# Repository Guidelines

## Project Structure & Module Organization
- `backend/app/main.py` runs the FastAPI app; feature routers live in `backend/app/api/` (papers, rubrics), shared config in `backend/app/core/`, ORM models in `backend/app/models/`, Pydantic schemas in `backend/app/schemas/`, and business helpers in `backend/app/services/`. Tests belong in `backend/app/tests/`.
- Database defaults to SQLite at `backend/prompt_trainer.db`; override via `.env` (`DATABASE_URL`) and keep `.env` local.
- Frontend is a Vite + React + TypeScript app in `frontend/`; components in `frontend/src/components/`, API client in `frontend/src/services/api.ts`, styles in `frontend/src/App.css` and `frontend/src/index.css`. Planning docs sit in `docs/`.

## Build, Test, and Development Commands
- Backend setup: `cd backend && source venv/bin/activate && pip install -r requirements.txt`.
- Run API (reload): `uvicorn app.main:app --reload` (uses `ALLOWED_ORIGINS` for CORS; defaults to `http://localhost:5173`).
- Backend tests: `cd backend && source venv/bin/activate && pytest`.
- Frontend install: `cd frontend && npm install`.
- Frontend dev server: `npm run dev` (defaults to `http://localhost:5173`; set `VITE_API_URL=http://127.0.0.1:8000` to point at the API).
- Frontend build/lint/preview: `npm run build`, `npm run lint`, `npm run preview`.

## Coding Style & Naming Conventions
- Python: follow PEP 8 (4-space indents, type hints). Keep FastAPI routers scoped by domain in `app/api/`; models and schemas use PascalCase class names with snake_case attributes matching DB columns. Place shared configuration in `app/core/`.
- TypeScript/React: functional components with PascalCase filenames; hook calls at the top of components. Keep API shapes in `src/services/api.ts` and reuse them in props. Prefer TypeScript types over `any`.
- Keep docstrings/comments instructional (as in existing modules) and avoid speculative TODOs.

## Testing Guidelines
- Place backend tests under `backend/app/tests/` with `test_*.py` filenames mirroring module paths. Use `DATABASE_URL=sqlite:///./prompt_trainer_test.db` (or an in-memory URL) to avoid mutating `prompt_trainer.db`; clean tables between tests via `drop_all_tables()` or SQLAlchemy session rollbacks.
- Exercise FastAPI routes end-to-end with `fastapi.testclient.TestClient` where possible; seed minimal fixtures (papers, rubrics, criteria) per test to keep state isolated.
- No frontend tests yet; at minimum run `npm run lint` and consider adding Vitest/RTL aligned with the Vite setup.

## Commit & Pull Request Guidelines
- Keep commit subjects short and present-tense; existing history favors concise summaries and occasional Conventional Commit prefixes (`feat:`, `docs:`, `chore:`). Group related changes per commit.
- PRs should describe scope, testing performed (`pytest`, `npm run lint`, manual API checks), and any schema or environment impacts (noting `DATABASE_URL`, `ALLOWED_ORIGINS`, `VITE_API_URL`). Include screenshots/GIFs for UI changes and link related issues.
- Avoid committing generated artifacts (`dist`, `.venv`, coverage output) and local databases unless explicitly required.

## Security & Configuration Tips
- Keep secrets in `.env` and out of version control; configure `DATABASE_URL` for your environment (use per-developer SQLite files) and tighten `ALLOWED_ORIGINS` in non-local setups.
- For the frontend, store the backend base URL in `VITE_API_URL` rather than hardcoding endpoints. When toggling CORS or DB settings, mirror changes in deployment notes or PR descriptions.

# Overview
I'm a product manager with limited coding experience who's looking to learn to become more technical. When you're coding and doing your work, please share tips that explain the tech architecture and any changes that you're making and why.

## Doc Rules
- All documents created must be put into the docs/ directory.
- Each document must have a clear and descriptive title.
- Use Markdown syntax for formatting.
- Include a table of contents for documents longer than 500 words.
- Use headings and subheadings to organize content.

## Product Backlog
- The product backlog is located at docs/backlog.md
- The product Plan is located at docs/project-plan.md
- Document sprint progress in docs/sprint1/sprint-1-progress.md, docs/sprint-2-progress.md, etc.

## Model
- For prompt building testing, we will use Qwen/Qwen3-0.6B model you can download from huggensface.
- For output testing, we will use the google/gemma-1.1-2b-it model you can download from huggensface.

## Database
- We will use a PostgreSQL database for storing user data and product information.
- The database schema will be designed to optimize for read and write performance.

## Git Management
- We will use Git for version control.
- The main branch will be protected, and all changes must go through a pull request.
- Use feature branches for new features and bug fixes.
- Commit messages should be clear and descriptive.
- Use .gitignore to exclude unnecessary files from the repository and large files.
- Push the changes to github after each iteration to ensure we can role back for any mistake.

## Latest Changes (Sprint 1 hardening)
- Added regression tests in `backend/app/tests/test_sprint1_endpoints.py` that cover health, paper CRUD, rubric CRUD, and criterion guard using a temp SQLite DB.
- Switched FastAPI lifecycle to `lifespan` and made timestamps timezone-aware to remove deprecation warnings.
- Fixed frontend builds by using type-only imports for API types in new components.

## Sprint 2 Planning Updates
- Backlog Sprint 2 now focuses on: paper submission UI + list, rubric builder with yes/no scoring, rubric selection on submit, and UI validation/feedback.
- Project plan Month 2 Week 5-6 updated to highlight the Paper & Rubric management deliverables above.

## Sprint 2 In-Progress Changes
- Papers can now be optionally associated with a rubric (backend `rubric_id` + `rubric_name` in responses); validation ensures rubric exists when provided.
- Paper list/detail responses expose submission_date/created_at (no updated_at), and frontend types/UX were aligned.
- Paper submission form now includes a rubric selector fed by `rubricApi.list()`.
- Progress is tracked in `docs/sprint-2-progress.md` (Week 1 summary added).
- Added toast notifications (success/error/info) in the frontend; PaperForm and RubricForm now surface status via toasts in addition to inline messages.
- Stubbed Evaluation API (`POST /api/evaluations/`) creates evaluation records, auto-creates a default prompt if none provided, and generates a simple model_response. Covered by pytest.
- Frontend can now trigger evaluation creation from the Papers list (uses the stubbed API); evaluate button appears when a paper has a rubric.
- Added an Evaluations tab to list evaluation results from the backend (via evaluationApi.list()).
- Evaluation list auto-refreshes when a new evaluation is created (listens for `evaluationCreated` events from the Papers list).
- Added negative tests for evaluation creation to ensure 404 responses for missing paper/rubric IDs.
- Navigation is wired to tab state (Papers/Rubrics/Evaluations) so the header controls the active section.
- Evaluation responses now include paper/rubric names and the frontend shows titles instead of just IDs.

## Sprint 3 In-Progress
- Progress tracked in `docs/sprint-3-progress.md` (focus: model integration, evaluation engine wiring, error handling).
- MI-001: Model abstraction layer implemented with `StubModelAdapter`; evaluation API now calls the adapter. Unit tests added for the adapter and end-to-end evaluation flow.
