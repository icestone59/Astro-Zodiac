#!/usr/bin/env bash
set -euo pipefail
python migration_runner.py
exec uvicorn api_app:app --host 0.0.0.0 --port "${PORT:-10000}"
