#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
if [ -x .venv/bin/pytest ]; then
  PYTEST=.venv/bin/pytest
else
  PYTEST=pytest
fi
"$PYTEST" -m "not student and not load"
