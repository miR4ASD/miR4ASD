"""Base Page Object containing common navigation and component handlers."""

from playwright.sync_api import Page


class BasePage:
    """Represents common page layout, tab navigation, and shared components."""

    TAB_SELECTORS = {
        "about": "#about-tab",
        "expression": "#expression-tab",
        "genetic": "#genetic-tab",
        "targets": "#targets-tab",
        "enrichment": "#enrichment-tab",
    }

    def __init__(self, page: Page, base_url: str):
        """
        Initialize with a Playwright Page and target base URL.

        Args:
            page: Playwright Page instance.
            base_url: Root URL under test.
        """
        self.page = page
        self.base_url = base_url

    def navigate(self) -> None:
        """Navigate to the base URL and wait for DOM readiness."""
        self.page.goto(self.base_url, wait_until="domcontentloaded", timeout=60000)
        self.page.wait_for_timeout(1000)

    def switch_tab(self, tab_name: str) -> None:
        """
        Switch to a designated navbar tab.

        Args:
            tab_name: One of 'about', 'expression', 'genetic', 'targets', 'enrichment'.
        """
        selector = self.TAB_SELECTORS.get(tab_name)
        if not selector:
            raise ValueError(f"Unknown tab name: {tab_name}")
        tab_elem = self.page.locator(selector)
        tab_elem.click()
        self.page.wait_for_timeout(500)

    def open_filter_drawer(self) -> None:
        """Open the slide-over advanced filter drawer."""
        self.page.locator(
            ".tab-pane.active .btn-filter, .btn-filter:visible"
        ).first.click()
        self.page.wait_for_selector("#filterDrawer.open", timeout=5000)

    def close_filter_drawer(self) -> None:
        """Close the slide-over filter drawer."""
        self.page.locator("#closeFilterDrawer").click()
        self.page.wait_for_timeout(300)

    def get_toast_message(self) -> str:
        """Retrieve current text content of the warning toast message."""
        toast_body = self.page.locator("#selectionWarningToastMsg")
        if toast_body.is_visible():
            return toast_body.inner_text().strip()
        return ""
