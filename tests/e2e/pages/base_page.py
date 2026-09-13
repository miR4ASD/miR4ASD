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
        "help": "#help-tab",
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
            tab_name: One of 'about', 'expression', 'genetic', 'targets', 'enrichment', 'help'.
        """
        selector = self.TAB_SELECTORS.get(tab_name)
        if not selector:
            raise ValueError(f"Unknown tab name: {tab_name}")
        tab_elem = self.page.locator(selector)
        tab_elem.click()
        self.page.wait_for_timeout(500)

    def is_tab_active(self, tab_name: str) -> bool:
        """Check if designated tab pane is currently active."""
        pane = self.page.locator(f"#{tab_name}.tab-pane.active")
        return pane.is_visible()

    def ensure_filter_card_expanded(self, selector: str) -> None:
        """
        Expand the enclosing per-tab filter card if it is currently collapsed.

        The per-tab filter inputs live in a Bootstrap collapse region that is
        hidden by default; the card header's ``Filters`` button reveals them.
        This is a no-op when the input is already visible.
        """
        loc = self.page.locator(selector)
        if loc.is_visible():
            return
        toggle = loc.locator(
            "xpath=ancestor::div[contains(@class, 'filter-card-inline')]"
            "[1]//button[@data-bs-toggle='collapse']"
        ).first
        toggle.click()
        self.page.wait_for_timeout(400)
        loc.wait_for(state="visible", timeout=5000)

    def is_filter_card_collapsed(self, selector: str) -> bool:
        """Return True if the input at ``selector`` is currently collapsed/hidden."""
        return not self.page.locator(selector).is_visible()

    def toggle_filter_card(self, tab_name: str) -> None:
        """Click the per-tab ``Filters`` header toggle to expand or collapse inputs."""
        self.page.locator(f"[data-bs-target='#{tab_name}FiltersCollapse']").click()
        self.page.wait_for_timeout(400)

    def fill_filter_input(self, selector: str, text: str) -> None:
        """
        Fill a per-tab inline filter input/textarea and wait for debounced apply.

        Args:
            selector: CSS selector of the filter input or textarea.
            text: Text to enter (may contain multiple newline/comma separated tokens).
        """
        self.ensure_filter_card_expanded(selector)
        self.page.locator(selector).fill(text)
        self.page.wait_for_timeout(400)

    def select_filter_option(self, selector: str, option: str) -> None:
        """
        Select a per-tab inline filter <select> option by value.

        Args:
            selector: CSS selector of the filter select element.
            option: Option value to select ('' for the default/All option).
        """
        self.ensure_filter_card_expanded(selector)
        self.page.locator(selector).select_option(option)
        self.page.wait_for_timeout(400)

    def click_back_to_top(self) -> None:
        """Click floating back to top button."""
        self.page.locator("#btn-back-to-top").click()
        self.page.wait_for_timeout(500)

    def is_back_to_top_visible(self) -> bool:
        """Check if back-to-top button is visible."""
        return self.page.locator("#btn-back-to-top").is_visible()

    def get_toast_message(self) -> str:
        """Retrieve current text content of the warning toast message."""
        toast_body = self.page.locator("#selectionWarningToastMsg")
        if toast_body.is_visible():
            return toast_body.inner_text().strip()
        return ""

    def dismiss_toast(self) -> None:
        """Dismiss warning toast by clicking close button."""
        self.page.locator("#selectionWarningToast .btn-close").click()
        self.page.wait_for_timeout(300)
