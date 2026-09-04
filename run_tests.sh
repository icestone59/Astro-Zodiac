#!/usr/bin/env bash
set -euo pipefail
PYTHONPATH=. python -m pytest -q tests/test_t13_auth_membership.py
