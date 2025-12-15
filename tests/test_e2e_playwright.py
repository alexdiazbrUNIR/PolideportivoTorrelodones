import subprocess
import time
import requests
import os
import signal
import pytest
import importlib

# Skip entire module if Playwright is not available
playwright_available = importlib.util.find_spec("playwright") is not None

SERVER_URL = 'http://127.0.0.1:5000'


def wait_for_server(url, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url, timeout=1)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


import pytest


@pytest.fixture(scope='session')
def live_server():
    # If server already running use it, else start run.py
    if wait_for_server(SERVER_URL, timeout=2):
        yield
        return

    proc = subprocess.Popen(['python', 'run.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        assert wait_for_server(SERVER_URL, timeout=15), 'Server did not start in time'
        yield
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


@pytest.mark.skipif(not playwright_available, reason="Playwright not installed — E2E tests skipped in this environment")
def test_full_user_flow_and_cancel(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # 1. Open home
        page.goto(SERVER_URL)
        assert 'Polideportivo' in page.title() or 'Polideportivo' in page.inner_text('body')

        # 2. Click first 'Reservar' button for first installation
        page.click('a.btn:has-text("Reservar")')
        # Wait for page to load
        page.wait_for_selector('.fecha-btn')

        # 3. Choose first date
        page.click('.fecha-btn')
        page.wait_for_selector('.hora-slot')

        # 4. Click first available slot
        slots = page.query_selector_all('.hora-slot.disponible')
        assert len(slots) > 0, 'No available slots found to book'
        slots[0].click()

        # 5. Fill form
        page.wait_for_selector('#formReserva')
        page.fill('#nombre', 'E2E Tester')
        test_email = f'e2e+{int(time.time())}@example.com'
        page.fill('#email', test_email)
        page.click('#formReserva button[type="submit"]')

        # 6. Wait for success message and presence of cancel link
        page.wait_for_selector('#mensajeExito')
        cancel_link = page.query_selector('#mensajeExito a')
        assert cancel_link is not None
        cancel_href = cancel_link.get_attribute('href')

        # 7. Navigate to cancel page and confirm cancellation
        page.goto(cancel_href)
        page.wait_for_selector('#btnCancelar')
        page.click('#btnCancelar')
        page.wait_for_selector('#mensaje')
        text = page.inner_text('#mensaje')
        assert 'cancelada' in text.lower() or 'cancelada' in text

        # 8. Verify reservation no longer present in mis_reservas
        page.goto(f"{SERVER_URL}/mis_reservas")
        page.fill('#emailSearch', test_email) if page.query_selector('#emailSearch') else None
        # try API directly
        r = requests.get(f"{SERVER_URL}/api/mis_reservas?email={test_email}")
        assert r.status_code == 200
        assert r.json() == []

        context.close()
        browser.close()
