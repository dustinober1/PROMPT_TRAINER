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
- `MI-003`: Basic error handling for model calls (partial; Ollama errors raise RuntimeError).

## Next Up
- Add error-handling paths/tests for adapter failures (MI-003) and surface clearer API errors.
- Expose provider selection config in settings (env) for easy switching in deployments.
