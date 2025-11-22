# Sprint 3 Progress

## Overview
- **Status**: In progress
- **Focus**: Model integration (adapter layer), evaluation engine wiring, and robust error handling.

## Goals
- Implement a model abstraction layer to support multiple providers (local and API-based).
- Wire the evaluation endpoint to call the adapter (stubbed initially).
- Handle model call errors gracefully (timeouts, connection issues).

## Current Scope
- `MI-001`: Model abstraction layer. ✅ StubModelAdapter implemented with interface + unit tests; evaluation endpoint now calls the adapter.
- `MI-002`: Ollama local model integration. ✅ OllamaAdapter added (config via OLLAMA_ENABLED/OLLAMA_BASE_URL/OLLAMA_MODEL) with tests for adapter selection.
- `PE-003`: Evaluation engine sends paper + rubric to model and stores structured response (via adapter).
- `MI-003`: Basic error handling for model calls. ✅ Adapter failures propagate as HTTP 502 from the evaluation API and are covered by tests; health exposes adapter name.
- Stub evaluations now include per-criterion names/scores and are rendered in the Evaluations tab; UI shows adapter badge and clearer error toasts.
- Feedback: Evaluations tab supports “Mark Correct/Incorrect” (updates is_correct on evaluation) with toasts.
- Prompts: Minimal prompt versioning API (create/list with parent-based version increment).

## Next Up
- Document provider selection config (env/settings) and add README snippet. ✅ Added.
- Consider a simple provider status badge in the UI header (currently shows adapter from /health). ✅ Adapter badge added.
