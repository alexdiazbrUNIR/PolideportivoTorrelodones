#!/usr/bin/env bash
python -m pip install --upgrade pip
pip install -r requirements-tests.txt
# If Playwright is installed, install browser binaries
if command -v playwright >/dev/null 2>&1; then
  playwright install --with-deps
fi
pytest -q --maxfail=1 --disable-warnings
