#!/usr/bin/env bash
python -m pip install --upgrade pip
pip install -r requirements-tests.txt
if command -v playwright >/dev/null 2>&1; then
  playwright install --with-deps
fi
pytest -q tests/test_e2e_playwright.py -k "not slow" --maxfail=1 --disable-warnings
