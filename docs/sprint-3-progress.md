# Sprint 3 Progress

## Overview
- **Status**: In progress
- **Focus**: Model integration (adapter layer), evaluation engine wiring, and robust error handling.

## Goals
- Implement a model abstraction layer to support multiple providers (local and API-based).
- Wire the evaluation endpoint to call the adapter (stubbed initially).
- Handle model call errors gracefully (timeouts, connection issues).

## Current Scope
- `MI-001`: Model abstraction layer.
- `MI-002`: Ollama local model integration (stub for now).
- `PE-003`: Evaluation engine sends paper + rubric to model and stores structured response.
- `MI-003`: Basic error handling for model calls.

## Next Up
- Add backend model adapter interface and stub provider.
- Update evaluation API to use the adapter instead of inline stubs.
- Expand pytest coverage for model-call failures and successful stub responses.
