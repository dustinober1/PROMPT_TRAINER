#!/usr/bin/env bash
# Development helper to start backend (FastAPI) and frontend (Vite) together.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_LOG="$ROOT_DIR/.dev-backend.log"
FRONTEND_LOG="$ROOT_DIR/.dev-frontend.log"

BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  if [[ -n "${BACKEND_PID}" ]] && kill -0 "${BACKEND_PID}" 2>/dev/null; then
    kill "${BACKEND_PID}" || true
  fi
  if [[ -n "${FRONTEND_PID}" ]] && kill -0 "${FRONTEND_PID}" 2>/dev/null; then
    kill "${FRONTEND_PID}" || true
  fi
}
trap cleanup EXIT INT TERM

if [[ ! -d "${BACKEND_DIR}/venv" ]]; then
  echo "Backend venv not found at ${BACKEND_DIR}/venv. Create it and install deps first." >&2
  exit 1
fi

if [[ ! -d "${FRONTEND_DIR}/node_modules" ]]; then
  echo "Frontend node_modules missing. Run 'cd frontend && npm install' first." >&2
  exit 1
fi

echo "Starting backend (FastAPI + uvicorn)..."
(
  cd "${BACKEND_DIR}"
  # shellcheck disable=SC1091
  source venv/bin/activate
  uvicorn app.main:app --reload > "${BACKEND_LOG}" 2>&1
) &
BACKEND_PID=$!

echo "Starting frontend (Vite dev server)..."
(
  cd "${FRONTEND_DIR}"
  npm run dev -- --host > "${FRONTEND_LOG}" 2>&1
) &
FRONTEND_PID=$!

echo "Backend running on http://127.0.0.1:8000 (logs: ${BACKEND_LOG})"
echo "Frontend running on http://localhost:5173 (logs: ${FRONTEND_LOG})"
echo "Press Ctrl+C to stop both."

wait "${BACKEND_PID}" "${FRONTEND_PID}"
