# Sprint 4 Plan - Results & Feedback

## Table of Contents
- [Overview](#overview)
- [Objectives](#objectives)
- [Workstreams & Tasks](#workstreams--tasks)
- [Timeline](#timeline)
- [Risks & Mitigations](#risks--mitigations)
- [Definition of Done](#definition-of-done)

## Overview
- Status: Planned; Duration: 2 weeks (Results & Feedback).
- Goal: Ship user-facing evaluation results and feedback capture to close the loop started in Sprint 3.
- Success: Backlog items PE-004 and FC-001 through FC-005 delivered with tests across backend and frontend.

## Objectives
- PE-004: Display evaluation results to user (rich, per-criterion detail).
- FC-001: Build feedback interface (correct/incorrect plus corrections).
- FC-002/FC-003: Allow marking evaluations correct or incorrect with persisted state.
- FC-004: Collect corrected score from user (per criterion or overall).
- FC-005: Store feedback entries in database for later analysis.

## Workstreams & Tasks
### Backend API & Data
- [ ] Add Feedback model/table linked to evaluation, rubric, and optional criterion; include corrected score/value, user note, timestamps; wire to Alembic migration.
- [ ] Extend evaluation detail payload to return rubric criteria, model scores, and any saved feedback so UI can render a single source of truth.
- [ ] Create feedback endpoints: POST to submit/update per evaluation/criterion, GET list for evaluation, and PATCH hooks on evaluations to toggle is_correct while staying consistent with feedback rows.
- [ ] Harden validation: ensure rubric and criterion belong to evaluation, enforce scoring types (yes/no) for corrected scores, return 404/422 for invalid references.
- [ ] Add seed/default behavior for stub adapter so evaluations include criterion-level outputs even without a real model.

### Frontend UX
- [ ] Build evaluation detail panel that shows paper info, rubric name, adapter used, overall verdict, and per-criterion scores with clear pass/fail badges.
- [ ] Implement feedback UI: mark correct/incorrect, enter corrected scores per criterion, optional correction note, and show submitted feedback state inline.
- [ ] Add optimistic save and toast flows for feedback submissions and a refresh of evaluation list/detail on success.
- [ ] Add client-side validation (required corrected score when marking incorrect, disabled buttons while saving, visible errors from API).
- [ ] Preserve accessibility and responsiveness: keyboard operable controls, mobile-friendly stacking, and loading/empty states.

### QA, Observability, and Docs
- [ ] Backend tests for feedback CRUD, validation failures, and evaluation detail payload shape using SQLite test DB.
- [ ] Frontend checks: lint/build, manual test matrix for submit/edit feedback, error handling, and evaluation rendering for missing rubric/criteria edge cases.
- [ ] Telemetry/logging: log feedback submissions with evaluation ID and adapter to trace issues; keep PII minimal.
- [ ] Documentation: update README adapter/config notes if payload shape changes, create sprint progress updates once work starts.

## Timeline
- **Week 1**: Finalize schema/migration, implement backend endpoints and tests, ensure stub adapter emits per-criterion scores, expose enriched evaluation detail API.
- **Week 2**: Ship frontend UI/UX for results and feedback, wire API client, run QA (`pytest` plus `npm run lint && npm run build` and manual checks), fix regressions, prep sprint demo.

## Risks & Mitigations
- Schema changes may require DB reset; provide migration plus note to drop local SQLite before running.
- Model output shape drift (stub vs real adapter); define stable schema contract and add adapter-side defaults.
- Feedback UI complexity; start with minimal “correct/incorrect + corrected score” and iterate after baseline works.

## Definition of Done
- All backlog items PE-004 and FC-001–FC-005 met with passing automated tests.
- Evaluation results and feedback persist round-trip (API and UI) with clear success and error states.
- Docs updated to explain new feedback flow and any migration steps.
