"""Intermediate base Page Object for studies tables (Expression and Genetic)."""

import re
from typing import List

from playwright.sync_api import Locator, Page

from tests.e2e.pages.base_page import BasePage


class StudiesTablePage(BasePage):
    """Reusable page component for studies DataTables and global selection."""

    def __init__(
        self,
        page: Page,
        base_url: str,
        tab_name: str,
        table_id: str,
        row_check_class: str,
        select_all_class: str,
        container_id: str,
        data_table_attr: str,
    ):
        """
        Initialize the studies table page component with table-specific selectors.

        Args:
            page: Playwright Page instance.
            base_url: Base application URL.
            tab_name: Navbar tab name ('expression' or 'genetic').
            table_id: DataTable element ID ('expression-table' or 'other-table').
            row_check_class: Class name of row checkboxes ('expr-row-check' etc).
            select_all_class: Selector of master select-all checkbox.
            container_id: Selector of parent tab container (e.g. '#expression').
            data_table_attr: data-table attribute ('expression' or 'genetic').
        """
        super().__init__(page, base_url)
        self.tab_name = tab_name
        self.table_id = table_id
        self.row_check_class = row_check_class
        self.select_all_class = select_all_class
        self.container_id = container_id
        self.data_table_attr = data_table_attr

    def navigate_table(self) -> None:
        """Switch to studies tab and wait for row rendering."""
        self.switch_tab(self.tab_name)
        self.page.wait_for_selector(
            f"#{self.table_id} tbody tr input.{self.row_check_class}",
            timeout=15000,
        )

    def get_row_checkboxes(self) -> List[Locator]:
        """Return list of row checkboxes in current page view."""
        return self.page.locator(
            f"#{self.table_id} tbody tr input.{self.row_check_class}"
        ).all()

    def select_row_by_index(self, index: int) -> None:
        """
        Click checkbox for a specific table row by index.

        Args:
            index: 0-based row index.
        """
        checkbox = self.page.locator(
            f"#{self.table_id} tbody tr input.{self.row_check_class}"
        ).nth(index)
        checkbox.click()
        self.page.wait_for_timeout(400)

    def get_selected_count(self) -> str:
        """Return the selected miRNA count from the global nav pill."""
        text = self.page.locator("#global-nav-selected-text").inner_text().strip()
        match = re.search(r"(\d+)\s*Selected", text)
        return match.group(1) if match else "0"

    def get_targets_count(self) -> str:
        """Return the target gene count badge text from the global nav pill."""
        badge = self.page.locator("#global-nav-targets-text")
        if badge.is_visible():
            match = re.search(r"(\d+)", badge.inner_text().strip())
            return match.group(1) if match else "0"
        return "0"

    def get_run_enrichment_button_text(self) -> str:
        """Return the full text of the Target Genes Run Enrichment CTA."""
        btn = self.page.locator(
            ".btn-analyze-filtered[data-source-table='targets']"
        )
        return btn.inner_text().strip()


    def click_clear_selection(self) -> None:
        """Clear the global miRNA selection across all tables and tabs."""
        self.page.evaluate("window.clearMiRNASelection();")
        self.page.wait_for_timeout(500)

    def click_header_select_all(self) -> None:
        """Click master select-all checkbox in table header."""
        self.page.locator(self.select_all_class).click(force=True)
        self.page.wait_for_timeout(500)

    def is_header_select_all_checked(self) -> bool:
        """Check if master select-all checkbox is checked."""
        return self.page.locator(self.select_all_class).is_checked()

    def click_reset_filters(self) -> None:
        """Click the 'Reset Filters' link in the per-tab filter card header."""
        self.page.locator(f"{self.container_id} .btn-reset-table-filters").click()
        self.page.wait_for_timeout(500)

    def click_run_target_enrichment_button(self) -> None:
        """Click the Target Genes tab 'Run Target Enrichment' CTA."""
        self.switch_tab("targets")
        btn = self.page.locator(
            ".btn-analyze-filtered[data-source-table='targets']"
        )
        btn.click()
        self.page.wait_for_timeout(600)

    def click_run_enrichment(self) -> None:
        """Alias for click_run_target_enrichment_button."""
        self.click_run_target_enrichment_button()

    def is_run_enrichment_button_enabled(self) -> bool:
        """Check if the Target Genes Run Enrichment CTA is enabled."""
        btn = self.page.locator(
            ".btn-analyze-filtered[data-source-table='targets']"
        )
        return not btn.is_disabled() and "disabled" not in (
            btn.get_attribute("class") or ""
        )


    def get_row_count(self) -> int:
        """Return the number of visible rows on the current table page."""
        return self.page.locator(f"#{self.table_id} tbody tr").count()

    def get_filtered_total(self) -> int:
        """
        Parse the DataTables info text and return the total matching row count.

        Unlike ``get_row_count()`` (visible rows on the current page), this
        reflects the full post-filter dataset size from the "X of Y entries"
        caption, so it is not capped by pagination.
        """
        info = self.page.locator(f"#{self.table_id}_info").inner_text()
        m = re.search(r"of (\d+) entr(?:y|ies)", info)
        if m:
            return int(m.group(1))
        return self.get_row_count()

    def expand_row_details(self, index: int = 0) -> None:
        """
        Click child details toggle on row by index.

        Args:
            index: 0-based row index.
        """
        control = self.page.locator(
            f"#{self.table_id} tbody tr td.details-control"
        ).nth(index)
        control.click()
        self.page.wait_for_timeout(400)

    def is_child_row_visible(self) -> bool:
        """Check if any expandable child row details card is visible."""
        return self.page.locator(
            f"#{self.table_id} tbody tr.details, #{self.table_id} tbody tr.dt-hasChild"
        ).is_visible()

    def get_child_row_text(self) -> str:
        """Return text inside visible child row details."""
        child = self.page.locator(
            f"#{self.table_id} tbody tr.child, #{self.table_id} tbody tr.details + tr"
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
            f"button.dt-paging-button[aria-controls='{self.table_id}']"
            f":text-is('{page_num}'), "
            f"#{self.table_id}_paginate .paginate_button:text-is('{page_num}')"
        ).first
        btn.click()
        self.page.wait_for_timeout(500)
