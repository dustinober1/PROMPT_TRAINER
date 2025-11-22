# Sprint 6 Plan - Advanced Rubric Scoring & Enhanced Feedback

## Overview
- **Duration**: 2 weeks
- **Theme**: Multiple scoring types (Meets/Not Meets, Numerical), criterion descriptions, and enhanced feedback with explanations.
- **Backlog alignment**: RM-005, RM-006, RM-007, FC-006, enhanced UI-003.

## Goals
- Enable educators to use three distinct scoring methodologies: Yes/No (existing), Meets/Does Not Meet, and Numerical ranges.
- Add descriptive guidelines to criteria so the model has clear instructions for evaluation.
- Allow users to provide optional explanatory notes when correcting evaluations.
- Enhance form validation across all input flows to catch edge cases and improve UX.

## User Stories
- **As an educator**, I can create rubrics with "Meets/Does Not Meet" scoring so I can evaluate papers using standards-based grading. (RM-005)
- **As an educator**, I can create rubrics with numerical scoring (e.g., 0-10 points) so I can assign weighted point values to criteria. (RM-006)
- **As an educator**, I can add detailed descriptions/guidelines to each criterion so the model understands exactly what to look for. (RM-007)
- **As a grader**, I can include an explanation when marking an evaluation incorrect so the system can learn from context. (FC-006)
- **As a user**, I receive clear, actionable validation messages for all forms so I know exactly what to fix. (UI-003)

## Workstreams & Tasks

### Backend API & Data

#### RM-005: Meets/Does Not Meet Scoring
**Technical Context**: This is similar to Yes/No but uses educational standards language. The database model needs to support a new scoring type enumeration.

- **Data Model Changes**:
  - Extend the `scoring_type` enum in the Criterion model to include `"meets_not_meets"` (currently only supports `"yes_no"`).
  - Update the schema validation in `schemas/rubric.py` to accept the new type.
  - Migration: Create an Alembic migration to add the new enum value to the database.

- **API Endpoints**:
  - No new endpoints needed; existing rubric/criterion CRUD should handle the new type.
  - Update response serialization to properly return `scoring_type` in criterion details.

- **Evaluation Logic**:
  - Extend the model adapter prompt template to understand "Meets/Does Not Meet" criteria.
  - Update evaluation response parsing to accept `"meets"` or `"does_not_meet"` as valid criterion scores.
  - Store these values in the evaluation results JSONB field.

- **Testing**:
  - pytest: Create rubric with meets/not-meets criteria → evaluate paper → verify response parsing.
  - Test that model response validation rejects invalid values (e.g., "maybe").

#### RM-006: Numerical Scoring
**Technical Context**: Numerical scoring introduces ranges (min/max points). This requires additional fields in the Criterion model and more complex validation.

- **Data Model Changes**:
  - Add `scoring_type = "numerical"` to the enum.
  - Add nullable fields to Criterion: `min_score` (integer), `max_score` (integer).
  - Add validation: when `scoring_type="numerical"`, min_score and max_score must be present, min < max.

- **Schema Validation** (Pydantic):
  - Create a validator in `CriterionCreate` schema that enforces min/max when numerical.
  - Reject requests where min_score >= max_score.
  - Common ranges to document: 0-1, 0-5, 0-10, 0-100.

- **Evaluation Logic**:
  - Update prompt template to include score ranges: "Score this criterion from {min} to {max} points."
  - Parse numerical responses from the model and validate they fall within range.
  - If model returns out-of-range value, either clamp it or flag as error (decide which).

- **Feedback Corrections**:
  - Update feedback correction endpoint to accept numerical corrected_score values.
  - Validate corrected_score is within the criterion's min/max range.

- **Testing**:
  - pytest: Create numerical criterion (0-10) → evaluate → verify score is integer in range.
  - Test boundary cases: min=0, max=100, model returns 50.
  - Test validation: reject criterion with min=10, max=5.

#### RM-007: Criterion Descriptions/Guidelines
**Technical Context**: Descriptions help the LLM understand what each criterion means. This is a simple text field addition but critical for quality.

- **Data Model Changes**:
  - Add `description` field (Text, nullable) to Criterion model.
  - Migration: Add column to criteria table.

- **Schema Changes**:
  - Add `description: Optional[str]` to `CriterionCreate` and `CriterionResponse` schemas.
  - Add length validation: 0-2000 characters, reject script tags (reuse Sprint 5 sanitization).

- **Evaluation Logic**:
  - Inject criterion descriptions into the prompt template.
  - Example template format:
    ```
    Criterion: {criterion_name}
    Description: {criterion_description}
    Scoring: {scoring_type} ({min}-{max} points)
    ```

- **UI Impact**:
  - Rubric builder form needs a description textarea for each criterion.
  - Display descriptions in the evaluation results view so users can see what the model was judging against.

- **Testing**:
  - pytest: Create criterion with description → verify it's stored and returned.
  - Test sanitization: reject description containing `<script>`.
  - End-to-end: Create rubric with descriptions → evaluate → verify descriptions appear in prompt context.

#### FC-006: Optional Explanation Field for Corrections
**Technical Context**: When users mark evaluations incorrect, they can now explain *why*, giving richer data for future prompt improvements.

- **Data Model Changes**:
  - Add `explanation` field (Text, nullable) to Feedback model (if it exists) or to the evaluation table.
  - This should be optional—not all corrections need detailed explanation.

- **API Endpoints**:
  - Update the feedback/correction endpoint (e.g., `PUT /api/evaluations/{id}/feedback`).
  - Accept an optional `explanation` field in the request body.
  - Store explanation alongside corrected_score and is_correct.

- **Schema Validation**:
  - Add `explanation: Optional[str]` to feedback schemas.
  - Length limit: 0-1000 characters, sanitize for script tags.

- **Future-Proofing**:
  - Explanation data will be critical for Sprint 8's automatic prompt improvement.
  - Design the data structure to be easily queryable (indexed field if using Postgres).

- **Testing**:
  - pytest: Mark evaluation incorrect with explanation → verify stored.
  - Test without explanation → should still work (optional field).
  - Test length/sanitization validation.

#### Enhanced UI-003: Form Validation Improvements
**Technical Context**: While basic validation exists, this task focuses on edge cases and better error messages.

- **Backend Validation Enhancements**:
  - Rubric form: Ensure at least one criterion exists before allowing submission.
  - Criterion form: Validate numerical ranges, require description for complex rubrics.
  - Paper form: Validate paper content is not just whitespace.
  - Prompt form: Already done in Sprint 5, but add extra check for placeholder syntax.

- **Error Response Standardization**:
  - Ensure all validation errors return consistent 422 responses with `detail` arrays.
  - Format: `{"detail": [{"loc": ["body", "min_score"], "msg": "must be less than max_score"}]}`

- **Frontend Validation**:
  - Add client-side validation before submission to reduce round-trips.
  - Use React Hook Form validators or custom validation functions.
  - Show inline error messages below each field (already partially done).

- **Testing**:
  - pytest: Test edge cases for each form (empty rubrics, invalid ranges, etc.).
  - Frontend manual testing: Trigger validation errors and verify messages are clear.

### Frontend UX

#### Rubric Builder Enhancements (RM-005, RM-006, RM-007)
**Technical Context**: The rubric builder form needs to support selecting scoring types and conditional fields.

- **Scoring Type Selector**:
  - Add a dropdown/radio group for each criterion: "Yes/No", "Meets/Does Not Meet", "Numerical (0-X)".
  - When "Numerical" is selected, show min_score and max_score input fields.
  - Use conditional rendering: `{scoringType === 'numerical' && <div>...</div>}`.

- **Description Field**:
  - Add a textarea for criterion description.
  - Optional field, but provide placeholder text: "Describe what this criterion measures...".
  - Character counter: show remaining characters (max 2000).

- **UI Flow**:
  1. User creates new rubric (name + description).
  2. For each criterion:
     - Enter name (required).
     - Select scoring type (required).
     - If numerical: enter min/max (required, validated).
     - Enter description (optional).
  3. Submit → backend validates and creates.

- **Example UI Layout**:
  ```
  Criterion 1
  ┌─────────────────────────────────────┐
  │ Name: [Evidence Quality          ] │
  │ Type: [Numerical ▼]                │
  │ Range: [0] to [10] points          │
  │ Description:                        │
  │ ┌─────────────────────────────────┐ │
  │ │ Evaluates the quality and      │ │
  │ │ relevance of cited sources...  │ │
  │ └─────────────────────────────────┘ │
  │ (1500/2000 characters)             │
  └─────────────────────────────────────┘
  ```

- **Type Definitions** (TypeScript):
  ```typescript
  type ScoringType = 'yes_no' | 'meets_not_meets' | 'numerical';

  interface Criterion {
    name: string;
    scoring_type: ScoringType;
    min_score?: number;
    max_score?: number;
    description?: string;
  }
  ```

- **Testing**:
  - Manual: Create rubrics with each scoring type and verify submission.
  - Verify validation: try submitting numerical criterion without min/max.

#### Evaluation Results Display (RM-005, RM-006)
**Technical Context**: Results view needs to show different score formats based on scoring type.

- **Score Rendering Logic**:
  - Yes/No: Display "Yes" or "No" (existing).
  - Meets/Does Not Meet: Display "Meets Standard" or "Does Not Meet Standard".
  - Numerical: Display score as "X / Y points" (e.g., "7 / 10 points").

- **Component Structure** (example):
  ```tsx
  function CriterionScore({ criterion, score }) {
    switch (criterion.scoring_type) {
      case 'yes_no':
        return <Badge>{score ? 'Yes' : 'No'}</Badge>;
      case 'meets_not_meets':
        return <Badge>{score === 'meets' ? 'Meets' : 'Does Not Meet'}</Badge>;
      case 'numerical':
        return <span>{score} / {criterion.max_score} points</span>;
    }
  }
  ```

- **Color Coding**:
  - Positive scores (Yes, Meets, high numbers): green badge.
  - Negative scores (No, Does Not Meet, low numbers): red badge.
  - For numerical: consider yellow for mid-range scores.

- **Testing**:
  - Evaluate papers with each scoring type and verify display format.

#### Feedback Form Enhancement (FC-006)
**Technical Context**: Add an optional explanation textarea when users mark evaluations incorrect.

- **UI Changes**:
  - When user clicks "Mark Incorrect", show expanded form:
    1. Corrected score input (already exists).
    2. NEW: Optional explanation textarea.
    3. Submit button.

- **Flow**:
  ```
  [Mark Incorrect] clicked
    ↓
  ┌────────────────────────────────────┐
  │ What should the score be?          │
  │ [7] / 10 points                    │
  │                                    │
  │ Why was this incorrect? (optional) │
  │ ┌────────────────────────────────┐ │
  │ │ Model missed the key evidence │ │
  │ │ in paragraph 3...             │ │
  │ └────────────────────────────────┘ │
  │ (0/1000 characters)                │
  │                                    │
  │ [Cancel] [Submit Correction]       │
  └────────────────────────────────────┘
  ```

- **API Call**:
  ```typescript
  evaluationApi.submitFeedback(evalId, {
    is_correct: false,
    corrected_score: 7,
    explanation: "Model missed the key evidence in paragraph 3..."
  });
  ```

- **State Management**:
  - Use local state for explanation text.
  - Clear form after submission.
  - Show success toast: "Feedback submitted with explanation".

- **Testing**:
  - Submit feedback with and without explanation.
  - Verify character limit enforcement (1000 chars).

#### Form Validation UX (UI-003)
**Technical Context**: Improve validation messages and error handling across all forms.

- **Client-Side Validation**:
  - Use React Hook Form's validation rules:
    ```typescript
    <input
      {...register("min_score", {
        required: "Minimum score is required for numerical criteria",
        validate: (value) =>
          value < maxScore || "Minimum must be less than maximum"
      })}
    />
    ```

- **Error Display**:
  - Show errors inline below each field (red text).
  - Show error count in submit button: "Fix 3 errors to continue".
  - Scroll to first error on submit attempt.

- **Success Feedback**:
  - Toast notifications for successful submissions (already implemented).
  - Loading states on submit buttons: "Creating rubric..." with spinner.

- **Backend Error Handling**:
  - Parse 422 validation errors from FastAPI.
  - Map field names to form fields and display appropriately.

- **Testing**:
  - Try to submit each form with invalid data and verify error messages.
  - Verify errors clear when user fixes the issue.

### QA & Testing

#### Backend Testing (pytest)
- **Scoring Type Tests**:
  - Test creating criteria with each scoring type.
  - Test evaluation with meets/not-meets criteria.
  - Test numerical scoring with various ranges (0-1, 0-100).
  - Test validation: reject invalid numerical ranges.

- **Description Tests**:
  - Test criteria with/without descriptions.
  - Test description sanitization (reject script tags).
  - Test description length limits.

- **Feedback Tests**:
  - Test feedback with/without explanation.
  - Test explanation length limits.
  - Verify explanation is stored and retrievable.

- **Integration Tests**:
  - End-to-end: Create rubric with numerical criteria → evaluate → mark incorrect with explanation.
  - Verify all data flows correctly through the system.

#### Frontend Testing
- **Manual Testing Matrix**:
  - Create rubric with Yes/No criteria → evaluate → verify display.
  - Create rubric with Meets/Not Meets criteria → evaluate → verify display.
  - Create rubric with numerical criteria (0-10) → evaluate → verify display.
  - Submit feedback with explanation → verify stored.

- **Validation Testing**:
  - Try to create numerical criterion with min > max → should show error.
  - Try to submit description with 2001 characters → should show error.
  - Try to submit explanation with 1001 characters → should show error.

- **Responsive Testing**:
  - Test new rubric builder fields on mobile/tablet.
  - Verify explanation textarea is usable on small screens.

- **Lint & Build**:
  - Run `npm run lint` → should pass.
  - Run `npm run build` → should compile without errors.

#### Smoke End-to-End Test
1. Create a new rubric named "Essay Grading":
   - Criterion 1: "Thesis Clarity" (Yes/No)
   - Criterion 2: "Evidence Quality" (Numerical, 0-10), description: "Evaluates quality of sources"
   - Criterion 3: "Writing Style" (Meets/Does Not Meet)

2. Submit a sample paper with this rubric.

3. Verify evaluation shows:
   - Thesis Clarity: Yes/No result
   - Evidence Quality: X/10 points
   - Writing Style: Meets/Does Not Meet

4. Mark "Evidence Quality" as incorrect:
   - Change score from 6 to 8
   - Add explanation: "Model undervalued the peer-reviewed sources"
   - Submit feedback

5. Verify:
   - Feedback stored with explanation
   - Accuracy metric updates
   - Evaluation shows corrected score

### Documentation & Ops

#### README Updates
- **Scoring Types Section**:
  - Document all three scoring types with examples.
  - Explain when to use each type:
    - Yes/No: Binary criteria (e.g., "Has a thesis statement?")
    - Meets/Does Not Meet: Standards-based (e.g., "Meets Common Core standard XYZ")
    - Numerical: Weighted scoring (e.g., "Content quality: 0-10 points")

- **Criterion Descriptions**:
  - Explain the importance of detailed descriptions for model accuracy.
  - Provide examples of good descriptions:
    ```
    Good: "Evidence must include at least 3 peer-reviewed sources
           published within the last 5 years, properly cited in APA format."

    Poor: "Has good evidence"
    ```

#### Migration Guide
- **For Existing Users**:
  - Run database migration to add new fields.
  - Existing yes/no criteria will continue to work.
  - New scoring types available immediately after migration.

- **Migration Command** (if using Alembic):
  ```bash
  cd backend
  alembic revision --autogenerate -m "Add scoring types and descriptions"
  alembic upgrade head
  ```

#### Sprint Progress Document
- Create `docs/sprint-6-progress.md` to track daily progress.
- Update after each major milestone (scoring type implemented, UI complete, etc.).

## Risks & Mitigations

### Risk 1: Model Doesn't Return Numerical Scores Reliably
**Likelihood**: Medium
**Impact**: High
**Mitigation**:
- Use structured output formats (JSON) in the prompt.
- Add explicit instructions: "Return a numerical score between {min} and {max}".
- Implement fallback: if model returns text instead of number, use regex to extract.
- Test with multiple models (Ollama, OpenAI) to verify consistency.

### Risk 2: Too Many Scoring Types Confuse Users
**Likelihood**: Low
**Impact**: Medium
**Mitigation**:
- Provide clear descriptions in the UI: "Choose Yes/No for simple binary criteria..."
- Add help tooltips or info icons explaining each type.
- Show example use cases in the rubric builder.
- Default to Yes/No (simplest) if user doesn't specify.

### Risk 3: Numerical Range Validation Edge Cases
**Likelihood**: Medium
**Impact**: Low
**Mitigation**:
- Comprehensive pytest coverage of boundary cases (0-0, negative ranges, etc.).
- Clear error messages: "Minimum score (10) must be less than maximum score (5)".
- Frontend validation to catch errors before backend submission.

### Risk 4: Explanation Field Doesn't Get Used
**Likelihood**: Medium
**Impact**: Low (it's optional)
**Mitigation**:
- Make the field prominent in the UI with helpful placeholder text.
- Show examples: "e.g., 'Model missed the counterargument in paragraph 4'".
- Track usage metrics and encourage if underutilized.
- Design system to work without explanations (they're a bonus for future improvements).

### Risk 5: Database Migration Issues
**Likelihood**: Low
**Impact**: Medium
**Mitigation**:
- Test migration on a copy of the database first.
- Provide rollback instructions in documentation.
- For SQLite users, consider backup recommendation before migration.
- Use Alembic for controlled, versioned migrations.

## Definition of Done

### Backend
- [ ] Three scoring types (yes_no, meets_not_meets, numerical) supported in Criterion model.
- [ ] Numerical criteria require and validate min_score and max_score fields.
- [ ] Criterion description field added and sanitized.
- [ ] Feedback explanation field added and optional.
- [ ] All new fields covered by pytest tests.
- [ ] Validation errors return clear, actionable messages.
- [ ] Database migration script created and tested.

### Frontend
- [ ] Rubric builder allows selecting all three scoring types.
- [ ] Numerical scoring shows min/max input fields conditionally.
- [ ] Description textarea available for all criteria.
- [ ] Evaluation results display scores appropriately for each type.
- [ ] Feedback form includes optional explanation textarea.
- [ ] Form validation shows clear inline error messages.
- [ ] All forms handle backend validation errors gracefully.
- [ ] UI tested on desktop, tablet, and mobile viewports.

### Testing
- [ ] Backend: All pytest tests pass (existing + new).
- [ ] Frontend: `npm run lint` and `npm run build` pass.
- [ ] Manual smoke test completed successfully (see above).
- [ ] Edge cases tested (invalid ranges, missing descriptions, etc.).

### Documentation
- [ ] README updated with scoring types and examples.
- [ ] Migration instructions documented.
- [ ] `docs/sprint-6-progress.md` created and updated.
- [ ] Code comments added for complex validation logic.

### User Experience
- [ ] Creating a rubric with numerical criteria feels intuitive.
- [ ] Error messages are helpful and guide users to fix issues.
- [ ] Evaluation results are easy to read for all scoring types.
- [ ] Feedback with explanations submits smoothly.

## Technical Learning Notes

### Key Concepts for Product Managers

**1. Enum Types in Databases**
- An enum (enumeration) is a data type that consists of a set of predefined values.
- Example: `scoring_type` can only be 'yes_no', 'meets_not_meets', or 'numerical'.
- This prevents invalid data (e.g., someone can't set scoring_type to 'random_value').
- In PostgreSQL, enums are native types. In SQLite, they're implemented with CHECK constraints.

**2. Conditional Validation**
- Different scoring types require different fields (numerical needs min/max, others don't).
- We use Pydantic validators to enforce these rules before data reaches the database.
- This is "fail fast" design—catch errors immediately rather than storing bad data.

**3. JSON Schema Flexibility**
- Evaluation results are stored in JSONB (JSON Binary) format in Postgres.
- This allows us to store different score formats without changing the database schema.
- Example: One evaluation has `{"criterion_1": "yes"}`, another has `{"criterion_1": 7}`.
- Trade-off: Flexibility vs. strict typing. We handle this with validation layers.

**4. Client-Side vs. Server-Side Validation**
- **Client-side**: Fast feedback, better UX, but can be bypassed.
- **Server-side**: Security layer, ensures data integrity, slower feedback.
- Best practice: Do both. Client-side for UX, server-side for security.

**5. Textarea Character Counting**
- Showing remaining characters (e.g., "1500/2000") helps users stay within limits.
- Implemented with React state: `onChange` updates character count.
- Better UX than just rejecting on submit.

**6. Migration Strategy**
- Database migrations are version-controlled changes to the schema.
- Like Git for your database structure.
- Alembic creates migration files that can be run on any environment.
- Allows us to add fields without losing existing data.

## Success Metrics

### Quantitative
- [ ] All three scoring types work in production.
- [ ] 80%+ of new rubrics use criterion descriptions.
- [ ] 20%+ of corrections include explanations.
- [ ] Zero critical bugs related to scoring type validation.

### Qualitative
- [ ] Beta testers report that numerical scoring "feels natural".
- [ ] Users understand the difference between scoring types.
- [ ] Error messages reduce support questions about validation.

## Next Sprint Preview (Sprint 7)

Based on the backlog, Sprint 7 will focus on:
- **API Integration** (MI-004, MI-005): OpenAI and Anthropic API support.
- **Model Selection UI** (MI-006): Allow users to choose their model provider.
- **API Key Management** (MI-007): Secure storage and configuration.

This builds on Sprint 6's enhanced rubrics by allowing users to use commercial models for higher accuracy.

---

*Document Version: 1.0*
*Created: 2025-11-21*
*Sprint Start: TBD*
*Sprint End: TBD*
