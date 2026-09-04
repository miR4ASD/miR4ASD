"""Page Object for Genetic & Other Studies tab and selection controls."""

from typing import List

from playwright.sync_api import Locator

from tests.e2e.pages.base_page import BasePage


class GeneticPage(BasePage):
    """Page component for Genetic & Other Studies table and selection stepper."""

    def navigate_to_genetic(self) -> None:
        """Switch to Genetic & Other Studies tab and wait for row rendering."""
        self.switch_tab("genetic")
        self.page.wait_for_selector(
            "#other-table tbody tr input.gen-row-check", timeout=15000
        )

    def get_row_checkboxes(self) -> List[Locator]:
        """Return list of row checkboxes in current page view."""
        return self.page.locator("#other-table tbody tr input.gen-row-check").all()

    def select_row_by_index(self, index: int) -> None:
        """
        Click checkbox for a specific table row by index.

        Args:
            index: 0-based row index.
        """
        checkbox = self.page.locator("#other-table tbody tr input.gen-row-check").nth(
            index
        )
        checkbox.click()
        self.page.wait_for_timeout(400)

    def get_selected_count(self) -> str:
        """Return count text shown in the selection badge."""
        badge = self.page.locator(".gen-selected-count").first
        if badge.is_visible():
            return badge.inner_text().strip()
        return "0"

    def click_select_visible(self) -> None:
        """Click 'Select Visible' button for genetic studies table."""
        self.page.locator(".btn-select-all-visible[data-table='genetic']").click()
        self.page.wait_for_timeout(500)

    def click_clear_selection(self) -> None:
        """Click 'Clear Selection' button for genetic studies table."""
        self.page.locator(".btn-clear-selection[data-table='genetic']").click()
        self.page.wait_for_timeout(500)

    def click_header_select_all(self) -> None:
        """Click master select-all checkbox in genetic table header."""
        self.page.locator(".select-all-other").click(force=True)
        self.page.wait_for_timeout(500)

    def is_header_select_all_checked(self) -> bool:
        """Check if master select-all checkbox is checked."""
        return self.page.locator(".select-all-other").is_checked()

    def click_reset_filters(self) -> None:
        """Click 'Reset Filters' button in genetic studies toolbar."""
        self.page.locator("#genetic .btn-reset-table-filters").click()
        self.page.wait_for_timeout(500)

    def click_run_target_enrichment_button(self) -> None:
        """Click contextual 'Run Target Enrichment' CTA button."""
        btn = self.page.locator(".btn-analyze-filtered[data-source-table='genetic']")
        btn.click()
        self.page.wait_for_timeout(600)

    def is_run_enrichment_button_enabled(self) -> bool:
        """Check if Run Target Enrichment CTA button is active/clickable."""
        btn = self.page.locator(".btn-analyze-filtered[data-source-table='genetic']")
        return not btn.is_disabled() and "disabled" not in (
            btn.get_attribute("class") or ""
        )

    def search(self, query: str) -> None:
        """
        Filter table by typing query into DataTables search box.

        Args:
            query: Keyword to search.
        """
        search_input = self.page.locator("input[aria-controls='other-table']")
        search_input.fill(query)
        self.page.wait_for_timeout(500)

    def get_row_count(self) -> int:
        """Return number of visible rows in table body."""
        return self.page.locator("#other-table tbody tr").count()

    def expand_row_details(self, index: int = 0) -> None:
        """
        Click child details toggle on row by index.

        Args:
            index: 0-based row index.
        """
        control = self.page.locator("#other-table tbody tr td.details-control").nth(
            index
        )
        control.click()
        self.page.wait_for_timeout(400)

    def is_child_row_visible(self) -> bool:
        """Check if any expandable child row details card is currently visible."""
        return self.page.locator(
            "#other-table tbody tr.details, #other-table tbody tr.dt-hasChild"
        ).is_visible()

    def click_page(self, page_num: int) -> None:
        """
        Navigate to specific page in DataTables pagination.

        Args:
            page_num: Page number (1-indexed).
        """
        btn = self.page.locator(
            f"button.dt-paging-button:text-is('{page_num}'), "
            f"#other-table_paginate .paginate_button:text-is('{page_num}')"
        ).first
        btn.click()
        self.page.wait_for_timeout(500)
