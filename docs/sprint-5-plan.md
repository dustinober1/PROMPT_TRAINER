# Sprint 5 Plan - Prompt Management & Accuracy

## Overview
- **Duration**: 2 weeks
- **Theme**: Prompt versioning, manual editing, basic accuracy metric, responsive UX, and input sanitization.
- **Backlog alignment**: PI-001, PI-002, PI-003, AR-001, UI-002, SD-002.

## Goals
- Ship a usable prompt editor with version history and activation.
- Track and surface an accuracy metric (evaluations marked correct / total).
- Make the UI responsive for mobile/tablet.
- Harden input sanitization to reduce XSS/injection risk.

## User Stories
- As a grader, I can view and edit the active prompt so I can quickly tweak model behavior. (PI-003)
- As a grader, I can see past prompt versions and activate one, so I can revert or compare. (PI-002)
- As a system, I store prompt templates with structured placeholders for paper/rubric content. (PI-001)
- As a user, I see an overall accuracy percentage so I know if quality is improving. (AR-001)
- As a user on mobile/tablet, the app layout adapts without losing functionality. (UI-002)
- As a security-conscious user, inputs are validated/sanitized so malicious content cannot break the app. (SD-002)

## Workstreams & Tasks
### Backend API & Data
- Prompt schema and API
  - Add structured fields for placeholders (paper, rubric, examples) and enforce template_text non-empty (PI-001).
  - Extend prompt list/create to return version lineage and active flag; add an activation endpoint (PI-002).
  - Add prompt update endpoint for manual edits and soft validation to keep required placeholders present (PI-003).
  - Migration: ensure prompt version increments and only one active prompt is enforced.
- Accuracy metric
  - Add service/helper to compute accuracy: `correct_count / total` from evaluations.is_correct (AR-001).
  - Expose accuracy via a lightweight endpoint (e.g., GET /api/metrics/accuracy) and include adapter name and timestamp for context.
- Input sanitization
  - Validate text fields on create/update (papers, rubrics, prompts) with length/whitespace guards; reject disallowed HTML tags or strip them server-side (SD-002).
  - Add tests for rejecting malicious input (script tags, overly long fields).

### Frontend UX
- Prompt management UI
  - Build a Prompt page with: active prompt display, version list, edit form, activate button, and “created at / parent version” metadata (PI-002/003).
  - Add guarded save flows: warn on missing placeholders; show toasts and optimistic updates.
- Accuracy display
  - Add an accuracy badge/widget in the header/status bar showing % correct and last updated time (AR-001).
  - Handle empty-state (no evaluations yet) gracefully.
- Responsive layout
  - Audit key pages (Papers, Rubrics, Evaluations, Prompts) for mobile breakpoints; adjust grids/stacking and tap targets (UI-002).
  - Add basic accessibility checks (focus states, keyboard access for prompt actions).

### QA & Testing
- Backend: pytest for prompt activation/versioning, template validation, accuracy endpoint, and sanitization rejections.
- Frontend: lint/build plus manual test matrix (desktop + mobile viewport) for prompt editing/activation and accuracy widget.
- Smoke E2E: create paper/rubric → evaluate → mark correct/incorrect → verify accuracy updates and prompt edit persists.

### Documentation & Ops
- Update README with prompt management usage and new endpoints; note sanitization expectations.
- Note migration/reset steps for local SQLite if schema changes (or add Alembic migration).
- Capture sprint progress in `docs/sprint-5-progress.md` once execution starts.

## Risks & Mitigations
- Placeholder drift between backend validation and frontend editor → define a shared placeholder list and validate on both sides.
- Accuracy metric misreads due to missing feedback → display “needs feedback” hint when evaluations lack is_correct.
- Mobile UI regressions → prioritize a quick responsive pass early in the sprint.

## Definition of Done
- Prompt editor + version list + activation working end-to-end with validation and tests.
- Accuracy endpoint and UI badge reflect evaluation feedback in near-real time.
- Responsive layouts verified on mobile/tablet for main tabs.
- Sanitization guards in place and covered by tests; docs updated with new behavior.
