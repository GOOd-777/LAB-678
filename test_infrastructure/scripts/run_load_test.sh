#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

USERS="${USERS:-25}"
SPAWN="${SPAWN:-5}"
DURATION="${DURATION:-30s}"
HOST="${HOST:-http://127.0.0.1:8080}"

if [ -x .venv/bin/locust ]; then
  LOCUST=.venv/bin/locust
else
  LOCUST=locust
fi

"$LOCUST" \
  -f test_infrastructure/load_tests/locustfile.py \
  --headless \
  -u "$USERS" \
  -r "$SPAWN" \
  -t "$DURATION" \
  --host "$HOST" \
  --csv reports/locust
