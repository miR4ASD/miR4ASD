"""Pytest fixtures and configuration for end-to-end Playwright tests."""

import http.server
import socketserver
import threading
from typing import Generator, List

import pytest
from playwright.sync_api import Page, sync_playwright


class QuietHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """Silent HTTP handler preventing console noise during automated test runs."""

    def log_message(self, format, *args):
        """Suppress standard HTTP server access logging."""
        pass


def pytest_addoption(parser):
    """Add custom CLI options to pytest."""
    parser.addoption(
        "--live",
        action="store_true",
        default=False,
        help="Run E2E tests against live production deployment (https://miR4ASD.github.io/miR4ASD/)",
    )


def pytest_collection_modifyitems(items):
    """Automatically tag all tests inside tests/e2e with the e2e marker."""
    for item in items:
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)


@pytest.fixture(scope="session")
def base_url(request) -> Generator[str, None, None]:
    """Provide target base URL, launching dynamic local server if --live is not set."""
    if request.config.getoption("--live"):
        yield "https://miR4ASD.github.io/miR4ASD/"
        return

    # Start ephemeral local server on OS-assigned open port (port=0)
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("127.0.0.1", 0), QuietHTTPHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    url = f"http://127.0.0.1:{port}/"
    try:
        yield url
    finally:
        server.shutdown()


@pytest.fixture
def app_page(base_url: str) -> Generator[Page, None, None]:
    """Provide an isolated browser page instance with error monitoring."""
    page_errors: List[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1400, "height": 900},
            permissions=["clipboard-read", "clipboard-write"],
        )
        page = context.new_page()

        # Capture unhandled JavaScript exceptions
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        # Navigate to target app URL
        page.goto(base_url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(1000)

        yield page

        browser.close()

        # Verify no unhandled JavaScript exceptions were thrown during the test
        assert len(page_errors) == 0, (
            f"Uncaught page exceptions detected: {page_errors}"
        )
