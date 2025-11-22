# Sprint 6 Task Checklist

## Backend Tasks

### RM-005: Meets/Does Not Meet Scoring

#### Data Model
- [ ] Add `"meets_not_meets"` to scoring_type enum in Criterion model
- [ ] Update `schemas/rubric.py` to accept new scoring type
- [ ] Create Alembic migration for enum extension
- [ ] Run migration and verify schema update

#### Evaluation Logic
- [ ] Update model adapter prompt template for meets/not-meets criteria
- [ ] Add parsing logic for "meets" and "does_not_meet" responses
- [ ] Update evaluation result storage to handle new score format
- [ ] Add validation to reject invalid score values

#### Testing
- [ ] Write test: Create rubric with meets/not-meets criteria
- [ ] Write test: Evaluate paper with meets/not-meets criteria
- [ ] Write test: Verify response parsing rejects invalid values
- [ ] Write test: Verify meets/not-meets scores stored correctly

---

### RM-006: Numerical Scoring

#### Data Model
- [ ] Add `"numerical"` to scoring_type enum
- [ ] Add `min_score` field (Integer, nullable) to Criterion model
- [ ] Add `max_score` field (Integer, nullable) to Criterion model
- [ ] Create Alembic migration for new fields
- [ ] Run migration and verify schema update

#### Schema Validation
- [ ] Add Pydantic validator: when numerical, min/max required
- [ ] Add Pydantic validator: min_score < max_score
- [ ] Add validation: min_score and max_score must be integers
- [ ] Add validation: reject when numerical but min/max missing

#### Evaluation Logic
- [ ] Update prompt template to include score ranges
- [ ] Add parsing logic for numerical responses (extract integer)
- [ ] Add validation: returned score within min/max range
- [ ] Implement decision: clamp out-of-range scores OR flag as error
- [ ] Update evaluation result storage for numerical scores

#### Feedback Integration
- [ ] Update feedback endpoint to accept numerical corrected_score
- [ ] Add validation: corrected_score within criterion's range
- [ ] Update feedback storage to handle numerical values

#### Testing
- [ ] Write test: Create criterion with numerical scoring (0-10)
- [ ] Write test: Evaluate and verify score is integer in range
- [ ] Write test: Boundary case min=0, max=100, score=50
- [ ] Write test: Reject criterion with min=10, max=5
- [ ] Write test: Reject criterion with min=max
- [ ] Write test: Numerical criterion missing min_score
- [ ] Write test: Numerical criterion missing max_score
- [ ] Write test: Submit feedback with numerical corrected_score
- [ ] Write test: Reject out-of-range corrected_score

---

### RM-007: Criterion Descriptions

#### Data Model
- [ ] Add `description` field (Text, nullable) to Criterion model
- [ ] Create Alembic migration to add description column
- [ ] Run migration and verify schema update

#### Schema Changes
- [ ] Add `description: Optional[str]` to CriterionCreate schema
- [ ] Add `description: Optional[str]` to CriterionResponse schema
- [ ] Add length validation: 0-2000 characters
- [ ] Add sanitization: reject script tags in description
- [ ] Add validation: reject excessive whitespace-only descriptions

#### Evaluation Logic
- [ ] Update prompt template to include criterion descriptions
- [ ] Format template: criterion name + description + scoring type
- [ ] Test template rendering with/without descriptions
- [ ] Verify descriptions improve model context

#### Testing
- [ ] Write test: Create criterion with description
- [ ] Write test: Create criterion without description
- [ ] Write test: Verify description stored and returned
- [ ] Write test: Reject description with script tags
- [ ] Write test: Reject description exceeding 2000 chars
- [ ] Write test: End-to-end evaluation with descriptions
- [ ] Write test: Verify descriptions appear in prompt context

---

### FC-006: Optional Explanation Field

#### Data Model
- [ ] Determine storage location (Feedback model or Evaluation table)
- [ ] Add `explanation` field (Text, nullable)
- [ ] Create Alembic migration for explanation field
- [ ] Run migration and verify schema update

#### API Changes
- [ ] Update feedback/correction endpoint signature
- [ ] Add `explanation` parameter (optional) to request body
- [ ] Update endpoint to store explanation alongside feedback
- [ ] Ensure explanation is returned in response

#### Schema Validation
- [ ] Add `explanation: Optional[str]` to feedback request schema
- [ ] Add `explanation: Optional[str]` to feedback response schema
- [ ] Add length validation: 0-1000 characters
- [ ] Add sanitization: reject script tags in explanation

#### Testing
- [ ] Write test: Submit feedback with explanation
- [ ] Write test: Submit feedback without explanation
- [ ] Write test: Verify explanation stored correctly
- [ ] Write test: Verify explanation returned in response
- [ ] Write test: Reject explanation exceeding 1000 chars
- [ ] Write test: Reject explanation with script tags
- [ ] Write test: Retrieve evaluation and verify explanation present

---

### UI-003: Enhanced Form Validation

#### Backend Validation
- [ ] Rubric validation: ensure at least one criterion exists
- [ ] Criterion validation: check numerical ranges
- [ ] Paper validation: reject whitespace-only content
- [ ] Prompt validation: verify placeholder syntax (already done?)
- [ ] Standardize all validation errors to 422 format
- [ ] Ensure error responses include field location and message

#### Error Response Format
- [ ] Verify all endpoints return consistent 422 responses
- [ ] Format errors as: `{"detail": [{"loc": [...], "msg": "..."}]}`
- [ ] Test error response parsing in frontend

#### Testing
- [ ] Write test: Submit rubric with zero criteria
- [ ] Write test: Submit criterion with invalid numerical range
- [ ] Write test: Submit paper with only whitespace
- [ ] Write test: Submit each form with missing required fields
- [ ] Write test: Verify error response format consistency

---

## Frontend Tasks

### Rubric Builder UI (RM-005, RM-006, RM-007)

#### Scoring Type Selector
- [ ] Add scoring type dropdown/radio for each criterion
- [ ] Options: "Yes/No", "Meets/Does Not Meet", "Numerical"
- [ ] Update TypeScript types for ScoringType union
- [ ] Implement conditional rendering for numerical fields
- [ ] Add default selection (Yes/No) when creating new criterion

#### Numerical Range Inputs
- [ ] Create min_score input field (number type)
- [ ] Create max_score input field (number type)
- [ ] Show these fields only when scoring_type = "numerical"
- [ ] Add placeholder text: "0" for min, "10" for max
- [ ] Add inline helper text: "Score range (e.g., 0-10 points)"

#### Description Field
- [ ] Add description textarea for each criterion
- [ ] Make field optional with clear label
- [ ] Add placeholder: "Describe what this criterion measures..."
- [ ] Implement character counter (X/2000 characters)
- [ ] Update live as user types

#### Form State Management
- [ ] Update criterion form state to include new fields
- [ ] Handle conditional required fields (numerical needs min/max)
- [ ] Implement form reset after successful submission
- [ ] Handle multiple criteria in rubric builder

#### TypeScript Types
- [ ] Define ScoringType union type
- [ ] Update Criterion interface with new fields
- [ ] Update CriterionCreate request type
- [ ] Update CriterionResponse type
- [ ] Ensure type safety across components

#### Testing
- [ ] Manual: Create rubric with Yes/No criteria
- [ ] Manual: Create rubric with Meets/Not Meets criteria
- [ ] Manual: Create rubric with Numerical criteria
- [ ] Manual: Try submitting numerical without min/max (should error)
- [ ] Manual: Verify description character counter works
- [ ] Manual: Test rubric builder on mobile viewport

---

### Evaluation Results Display (RM-005, RM-006)

#### Score Rendering Component
- [ ] Create CriterionScore component with switch logic
- [ ] Implement Yes/No rendering (existing)
- [ ] Implement Meets/Does Not Meet rendering
- [ ] Implement Numerical rendering (X/Y points format)
- [ ] Add TypeScript props interface

#### Visual Styling
- [ ] Style Yes/No scores with badges (green/red)
- [ ] Style Meets/Not Meets with badges (green/red)
- [ ] Style Numerical scores with inline text + color
- [ ] Add color coding: green (good), yellow (mid), red (low)
- [ ] Ensure consistent spacing and alignment

#### Criterion Description Display
- [ ] Show description below criterion name in results
- [ ] Use muted/secondary text styling for description
- [ ] Handle criteria without descriptions gracefully
- [ ] Add expand/collapse for long descriptions (optional)

#### Testing
- [ ] Manual: Evaluate paper with Yes/No criteria, verify display
- [ ] Manual: Evaluate paper with Meets/Not Meets, verify display
- [ ] Manual: Evaluate paper with Numerical, verify X/Y format
- [ ] Manual: Verify descriptions appear correctly
- [ ] Manual: Test results view on mobile

---

### Feedback Form Enhancement (FC-006)

#### Explanation Textarea
- [ ] Add explanation textarea to feedback form
- [ ] Label: "Why was this incorrect? (optional)"
- [ ] Add character counter (X/1000 characters)
- [ ] Update live as user types
- [ ] Style consistently with other textareas

#### Form Layout
- [ ] Update feedback form to include explanation field
- [ ] Position below corrected score input
- [ ] Ensure form remains compact and usable
- [ ] Add helper text or placeholder example

#### API Integration
- [ ] Update evaluationApi.submitFeedback() call
- [ ] Include explanation in request body
- [ ] Handle optional field (send null if empty)
- [ ] Update TypeScript request interface

#### State Management
- [ ] Add explanation to form state
- [ ] Clear explanation after successful submission
- [ ] Handle explanation in form reset

#### Success Feedback
- [ ] Update success toast when explanation included
- [ ] Message: "Feedback submitted with explanation"
- [ ] Or: "Feedback submitted" (if no explanation)

#### Testing
- [ ] Manual: Submit feedback with explanation
- [ ] Manual: Submit feedback without explanation
- [ ] Manual: Verify character limit (1001 chars should error)
- [ ] Manual: Verify explanation appears in backend
- [ ] Manual: Test feedback form on mobile

---

### Form Validation UX (UI-003)

#### Client-Side Validation Rules
- [ ] Add React Hook Form validation to rubric form
- [ ] Add validation to criterion name (required)
- [ ] Add validation to scoring type (required)
- [ ] Add conditional validation: numerical requires min/max
- [ ] Add validation: min < max for numerical
- [ ] Add validation: description length (0-2000)
- [ ] Add validation: explanation length (0-1000)

#### Error Display
- [ ] Show inline errors below each field (red text)
- [ ] Implement error summary at top of form
- [ ] Show error count in submit button
- [ ] Scroll to first error on submit attempt
- [ ] Clear errors when user fixes issue

#### Backend Error Handling
- [ ] Parse 422 validation errors from API
- [ ] Map error field locations to form fields
- [ ] Display backend errors inline with appropriate fields
- [ ] Handle generic errors with toast notification

#### Loading States
- [ ] Add loading spinner to submit buttons
- [ ] Change button text: "Creating rubric..." during submission
- [ ] Disable form inputs while submitting
- [ ] Handle submission errors gracefully

#### Testing
- [ ] Manual: Submit rubric form with empty criterion name
- [ ] Manual: Submit numerical criterion with min > max
- [ ] Manual: Submit description with 2001 characters
- [ ] Manual: Verify errors clear when fixed
- [ ] Manual: Test error scrolling behavior
- [ ] Manual: Test loading states

---

## Testing Tasks

### Backend pytest Suite
- [ ] Run all existing tests and ensure they pass
- [ ] Add tests for new scoring types (meets/not-meets, numerical)
- [ ] Add tests for criterion descriptions
- [ ] Add tests for feedback explanations
- [ ] Add tests for enhanced validations
- [ ] Achieve 70%+ code coverage for new code
- [ ] Run test suite: `cd backend && pytest`

### Frontend Lint & Build
- [ ] Run `npm run lint` and fix any issues
- [ ] Run `npm run build` and verify successful compilation
- [ ] Fix any TypeScript errors
- [ ] Fix any ESLint warnings

### Integration Testing
- [ ] Test full flow: Create numerical rubric → Evaluate → Review results
- [ ] Test feedback with explanation flow
- [ ] Test validation error flow from backend to frontend
- [ ] Test responsive layouts on multiple screen sizes

### Smoke End-to-End Test
- [ ] Create "Essay Grading" rubric (see plan for details)
- [ ] Add Thesis Clarity (Yes/No)
- [ ] Add Evidence Quality (Numerical 0-10) with description
- [ ] Add Writing Style (Meets/Does Not Meet)
- [ ] Submit sample paper with rubric
- [ ] Verify evaluation shows all three score formats
- [ ] Mark Evidence Quality incorrect with explanation
- [ ] Verify feedback stored and accuracy updated

---

## Documentation Tasks

### README Updates
- [ ] Add "Scoring Types" section
- [ ] Document Yes/No scoring with example
- [ ] Document Meets/Does Not Meet scoring with example
- [ ] Document Numerical scoring with example
- [ ] Explain when to use each scoring type
- [ ] Add "Criterion Descriptions" section
- [ ] Provide examples of good vs. poor descriptions
- [ ] Update API documentation (if separate)

### Migration Documentation
- [ ] Document migration process for existing users
- [ ] Provide Alembic migration commands
- [ ] Note that existing rubrics continue to work
- [ ] Explain backwards compatibility
- [ ] Add troubleshooting section for common issues

### Code Documentation
- [ ] Add docstrings to new Pydantic validators
- [ ] Comment complex validation logic
- [ ] Document scoring type enum values
- [ ] Add JSDoc comments to TypeScript interfaces
- [ ] Document component props interfaces

### Progress Tracking
- [ ] Create `docs/sprint-6-progress.md`
- [ ] Update daily with completed tasks
- [ ] Note any blockers or issues encountered
- [ ] Record decisions made during implementation
- [ ] Final update when sprint complete

---

## Risk Mitigation Tasks

### Model Numerical Scoring Reliability
- [ ] Test prompt with Ollama local models
- [ ] Test prompt with OpenAI (if available)
- [ ] Implement regex fallback for score extraction
- [ ] Add explicit numerical instructions to prompt template
- [ ] Test with edge cases (min=0, max=100)

### User Confusion Prevention
- [ ] Add help tooltips for each scoring type
- [ ] Provide example use cases in UI
- [ ] Create guided examples in documentation
- [ ] Default to simplest option (Yes/No)
- [ ] Add info icon with description for each type

### Edge Case Testing
- [ ] Test numerical range: 0-0 (should reject?)
- [ ] Test numerical range: negative values
- [ ] Test numerical range: very large numbers (0-10000)
- [ ] Test description with only whitespace
- [ ] Test explanation with only whitespace
- [ ] Test unicode/emoji in descriptions and explanations

### Database Migration Safety
- [ ] Backup database before migration
- [ ] Test migration on copy of production data
- [ ] Verify rollback procedure
- [ ] Test migration on fresh database
- [ ] Document recovery steps if migration fails

---

## Definition of Done Verification

### Backend Checklist
- [ ] All three scoring types work in database
- [ ] Numerical validation enforces min < max
- [ ] Descriptions stored and sanitized
- [ ] Explanations stored and optional
- [ ] All pytest tests pass
- [ ] Validation errors clear and actionable
- [ ] Migration script created and tested

### Frontend Checklist
- [ ] Scoring type selector works
- [ ] Numerical inputs show conditionally
- [ ] Description textarea functional
- [ ] Results display all scoring types correctly
- [ ] Explanation field in feedback form
- [ ] Inline validation errors show
- [ ] Mobile responsive layouts verified
- [ ] Lint and build pass

### Testing Checklist
- [ ] All backend tests pass
- [ ] All frontend lint/build checks pass
- [ ] Smoke test completed successfully
- [ ] Edge cases tested and documented
- [ ] No regressions in existing features

### Documentation Checklist
- [ ] README updated with scoring types
- [ ] Migration guide complete
- [ ] sprint-6-progress.md created
- [ ] Code comments added where needed
- [ ] API changes documented

---

## Task Assignment Template

For each task above, track:
- **Status**: Not Started / In Progress / Blocked / Complete
- **Assigned To**: [Developer name]
- **Estimated Time**: [Hours]
- **Actual Time**: [Hours]
- **Notes**: [Any relevant notes or blockers]

Example:
```
- [x] Add numerical to scoring_type enum
  Status: Complete
  Assigned: Dev A
  Estimated: 0.5h
  Actual: 0.75h
  Notes: Had to research Alembic enum migrations
```

---

*Total Estimated Tasks: 180+*
*Estimated Sprint Duration: 2 weeks (80 hours)*
*Tasks per day: ~12-15 tasks*
