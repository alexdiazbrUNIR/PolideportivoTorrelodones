# PowerShell script to set up test environment and run pytest
python -m pip install --upgrade pip
pip install -r requirements-tests.txt
# If Playwright is installed, install browser binaries
if (Get-Command playwright -ErrorAction SilentlyContinue) { playwright install --with-deps }
pytest -q --maxfail=1 --disable-warnings
