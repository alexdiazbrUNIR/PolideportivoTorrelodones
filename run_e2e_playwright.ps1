# Run only E2E Playwright tests (PowerShell)
python -m pip install --upgrade pip
pip install -r requirements-tests.txt
# Install Playwright browser binaries (may fail in restricted environments)
if (Get-Command playwright -ErrorAction SilentlyContinue) { playwright install --with-deps }
pytest -q tests/test_e2e_playwright.py -k "not slow" --maxfail=1 --disable-warnings
