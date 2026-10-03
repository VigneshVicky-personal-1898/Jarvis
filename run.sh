#!/usr/bin/env bash
# AI-ASSISTED: Cursor
# PROMPT: Start RAYA API and UI with venv fallback
# ACCEPTED-BY: vignesh

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WINDOWS=0
if [[ "${OSTYPE:-}" == msys* || "${OSTYPE:-}" == cygwin* || "${OS:-}" == "Windows_NT" ]]; then
  WINDOWS=1
fi

find_python() {
  if command -v python >/dev/null 2>&1; then
    echo "python"
    return
  fi
  if command -v python3 >/dev/null 2>&1; then
    echo "python3"
    return
  fi
  if command -v py >/dev/null 2>&1; then
    echo "py"
    return
  fi
  echo "Python 3 is required but was not found on PATH." >&2
  exit 1
}

PYTHON_CMD="$(find_python)"

if [[ "$WINDOWS" -eq 1 ]]; then
  VENV_PY="$ROOT/.venv/Scripts/python.exe"
  VENV_PIP="$ROOT/.venv/Scripts/pip.exe"
  VENV_UVICORN="$ROOT/.venv/Scripts/uvicorn.exe"
else
  VENV_PY="$ROOT/.venv/bin/python"
  VENV_PIP="$ROOT/.venv/bin/pip"
  VENV_UVICORN="$ROOT/.venv/bin/uvicorn"
fi

if [[ ! -f "$VENV_PY" ]]; then
  if [[ "$PYTHON_CMD" == "py" ]]; then
    py -3 -m venv "$ROOT/.venv"
  else
    "$PYTHON_CMD" -m venv "$ROOT/.venv"
  fi
fi

"$VENV_PY" -m pip install --upgrade pip >/dev/null
"$VENV_PY" -m pip install -r "$ROOT/requirements.txt"

if [[ ! -d "$ROOT/frontend/node_modules" ]] || [[ ! -f "$ROOT/frontend/node_modules/.bin/vite" && ! -f "$ROOT/frontend/node_modules/.bin/vite.cmd" ]]; then
  (cd "$ROOT/frontend" && npm install)
fi

"$VENV_PY" -m uvicorn main:app --host 127.0.0.1 --port 8765 --app-dir "$ROOT/backend" &
BACK_PID=$!

cleanup() {
  kill "$BACK_PID" 2>/dev/null || true
}
trap cleanup EXIT

echo "RAYA API: http://127.0.0.1:8765"
echo "RAYA UI:  http://127.0.0.1:5173"
cd "$ROOT/frontend" && npm run dev
