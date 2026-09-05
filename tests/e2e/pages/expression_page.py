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

    def click_select_visible(self) -> None:
        """Click 'Select Visible' button for expression table."""
        self.page.locator(".btn-select-all-visible[data-table='expression']").click()
        self.page.wait_for_timeout(500)

    def click_clear_selection(self) -> None:
        """Click 'Clear Selection' button for expression table."""
        self.page.locator(".btn-clear-selection[data-table='expression']").click()
        self.page.wait_for_timeout(500)

    def click_header_select_all(self) -> None:
        """Click master select-all checkbox in expression table header."""
        self.page.locator(".select-all-expr").click(force=True)
        self.page.wait_for_timeout(500)

    def is_header_select_all_checked(self) -> bool:
        """Check if master select-all checkbox is checked."""
        return self.page.locator(".select-all-expr").is_checked()

    def click_reset_filters(self) -> None:
        """Click 'Reset Filters' button in expression toolbar."""
        self.page.locator("#expression .btn-reset-table-filters").click()
        self.page.wait_for_timeout(500)

    def click_run_target_enrichment_button(self) -> None:
        """Click the contextual 'Run Target Enrichment' button."""
        btn = self.page.locator(".btn-analyze-filtered[data-source-table='expression']")
        btn.click()
        self.page.wait_for_timeout(600)

    def click_run_enrichment(self) -> None:
        """Alias for click_run_target_enrichment_button."""
        self.click_run_target_enrichment_button()

    def is_run_enrichment_button_enabled(self) -> bool:
        """Check if Run Target Enrichment button is enabled."""
        btn = self.page.locator(".btn-analyze-filtered[data-source-table='expression']")
        return not btn.is_disabled() and "disabled" not in (
            btn.get_attribute("class") or ""
        )

    def search(self, query: str) -> None:
        """
        Filter table by typing query into DataTables search box.

        Args:
            query: Keyword to search.
        """
        search_input = self.page.locator("input[aria-controls='expression-table']")
        search_input.fill(query)
        self.page.wait_for_timeout(500)

    def get_row_count(self) -> int:
        """Return number of visible rows in table body."""
        return self.page.locator("#expression-table tbody tr").count()

    def expand_row_details(self, index: int = 0) -> None:
        """
        Click child details toggle on row by index.

        Args:
            index: 0-based row index.
        """
        control = self.page.locator(
            "#expression-table tbody tr td.details-control"
        ).nth(index)
        control.click()
        self.page.wait_for_timeout(400)

    def is_child_row_visible(self) -> bool:
        """Check if any expandable child row details card is visible."""
        return self.page.locator(
            "#expression-table tbody tr.details, #expression-table tbody tr.dt-hasChild"
        ).is_visible()

    def get_child_row_text(self) -> str:
        """Return text inside visible child row details."""
        child = self.page.locator(
            "#expression-table tbody tr.child, #expression-table tbody tr.details + tr"
        ).first
        if child.is_visible():
            return child.inner_text()
        return ""

    def click_page(self, page_num: int) -> None:
        """
        Navigate to specific page in DataTables pagination.

        Args:
            page_num: Page number (1-indexed).
        """
        btn = self.page.locator(
            f"button.dt-paging-button[aria-controls='expression-table']"
            f":text-is('{page_num}'), "
            f"#expression-table_paginate .paginate_button:text-is('{page_num}')"
        ).first
        btn.click()
        self.page.wait_for_timeout(500)
