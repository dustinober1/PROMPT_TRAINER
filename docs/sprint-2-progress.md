# Sprint 2 Progress (Week 1)

## Overview
- **Status**: In progress
- **Focus**: Paper submission UX, rubric linkage, and alignment between backend and frontend types.

## What Shipped
- Papers can now be optionally associated with a rubric (`rubric_id` + `rubric_name` in responses).
- Paper responses expose submission and created timestamps; frontend types and UI now match the backend (no stale `updated_at`).
- Paper submission form includes a rubric selector populated from existing rubrics.
- Paper list/detail views surface rubric information and correct timestamps.
- Added toast notifications (success/error/info) for paper and rubric submissions so users get immediate feedback alongside inline messages.
- Stubbed Evaluation API (`POST /api/evaluations/`) that validates paper/rubric, auto-creates a default prompt if none exists, and returns a generated model_response; covered by pytest.
- Frontend Papers list now exposes an Evaluate button when a rubric is assigned, calling the stubbed Evaluation API for a quick end-to-end check.
- Evaluations tab added to the frontend to list evaluation results (uses Evaluation API list endpoint).
- Evaluations list auto-refreshes when a new evaluation is created (listens for `evaluationCreated` events).
- Added negative-path backend tests for evaluation creation (404 on missing paper/rubric IDs) to harden validation.
- Navigation is now bound to tab state (Papers/Rubrics/Evaluations) for consistent section switching.
- Evaluation responses now include paper/rubric names; the Evaluations tab shows titles instead of just IDs.

## Testing
- Backend: `cd backend && source venv/bin/activate && pytest` (passes; uses temp SQLite).
- Frontend: `cd frontend && npm run build` (passes).

## Notes and Tips
- The new `rubric_id` column requires a fresh database. For SQLite, delete `backend/prompt_trainer.db` or run `drop_all_tables()` then restart to recreate tables.
- API validation returns 404 if a provided `rubric_id` does not exist.
- Use `VITE_API_URL` to point the frontend at the running backend (default `http://127.0.0.1:8000`).

## Next Up
- Wire evaluation flow (paper + rubric submission to model stub).
- Add basic toasts/notifications around form submissions.
- Expand backend tests for additional paper/rubric edge cases.
