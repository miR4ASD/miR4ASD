"""Page Object for Expression Studies tab and miRNA selection controls."""

from typing import List

from playwright.sync_api import Locator

from tests.e2e.pages.base_page import BasePage


class ExpressionPage(BasePage):
    """Page component for Expression Studies table and selection stepper."""

    def navigate_to_expression(self) -> None:
        """Switch to Expression Studies tab and wait for row rendering."""
        self.switch_tab("expression")
        self.page.wait_for_selector(
            "#expression-table tbody tr input.expr-row-check", timeout=15000
        )

    def get_row_checkboxes(self) -> List[Locator]:
        """Return list of row checkboxes in current page view."""
        return self.page.locator(
            "#expression-table tbody tr input.expr-row-check"
        ).all()

    def select_row_by_index(self, index: int) -> None:
        """
        Click checkbox for a specific table row by index.

        Args:
            index: 0-based row index.
        """
        checkbox = self.page.locator(
            "#expression-table tbody tr input.expr-row-check"
        ).nth(index)
        checkbox.click()
        self.page.wait_for_timeout(400)

    def get_selected_count(self) -> str:
        """Return the count text shown in the selection badge."""
        badge = self.page.locator(".expr-selected-count").first
        if badge.is_visible():
            return badge.inner_text().strip()
        return "0"

    def click_run_target_enrichment_button(self) -> None:
        """Click the contextual 'Run Target Enrichment' button."""
        btn = self.page.locator(".btn-analyze-filtered[data-source-table='expression']")
        btn.click()
        self.page.wait_for_timeout(600)
