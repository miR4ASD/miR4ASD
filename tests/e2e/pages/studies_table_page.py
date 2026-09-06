"""Intermediate base Page Object for studies tables (Expression and Genetic)."""

from typing import List

from playwright.sync_api import Locator, Page

from tests.e2e.pages.base_page import BasePage


class StudiesTablePage(BasePage):
    """Reusable page component for studies DataTables and selection steppers."""

    def __init__(
        self,
        page: Page,
        base_url: str,
        tab_name: str,
        table_id: str,
        row_check_class: str,
        badge_class: str,
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
            badge_class: Selector of selection badge (e.g. '.expr-selected-count').
            select_all_class: Selector of master select-all checkbox.
            container_id: Selector of parent tab container (e.g. '#expression').
            data_table_attr: data-table attribute ('expression' or 'genetic').
        """
        super().__init__(page, base_url)
        self.tab_name = tab_name
        self.table_id = table_id
        self.row_check_class = row_check_class
        self.badge_class = badge_class
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
        """Return the count text shown in the selection badge."""
        badge = self.page.locator(self.badge_class).first
        if badge.is_visible():
            return badge.inner_text().strip()
        return "0"

    def click_select_visible(self) -> None:
        """Click 'Select Visible' button for studies table."""
        self.page.locator(
            f".btn-select-all-visible[data-table='{self.data_table_attr}']"
        ).click()
        self.page.wait_for_timeout(500)

    def click_clear_selection(self) -> None:
        """Click 'Clear Selection' button for studies table."""
        self.page.locator(
            f".btn-clear-selection[data-table='{self.data_table_attr}']"
        ).click()
        self.page.wait_for_timeout(500)

    def click_header_select_all(self) -> None:
        """Click master select-all checkbox in table header."""
        self.page.locator(self.select_all_class).click(force=True)
        self.page.wait_for_timeout(500)

    def is_header_select_all_checked(self) -> bool:
        """Check if master select-all checkbox is checked."""
        return self.page.locator(self.select_all_class).is_checked()

    def click_reset_filters(self) -> None:
        """Click 'Reset Filters' button in table toolbar."""
        self.page.locator(f"{self.container_id} .btn-reset-table-filters").click()
        self.page.wait_for_timeout(500)

    def click_run_target_enrichment_button(self) -> None:
        """Click contextual 'Run Target Enrichment' button."""
        btn = self.page.locator(
            f".btn-analyze-filtered[data-source-table='{self.data_table_attr}']"
        )
        btn.click()
        self.page.wait_for_timeout(600)

    def click_run_enrichment(self) -> None:
        """Alias for click_run_target_enrichment_button."""
        self.click_run_target_enrichment_button()

    def is_run_enrichment_button_enabled(self) -> bool:
        """Check if Run Target Enrichment button is enabled."""
        btn = self.page.locator(
            f".btn-analyze-filtered[data-source-table='{self.data_table_attr}']"
        )
        return not btn.is_disabled() and "disabled" not in (
            btn.get_attribute("class") or ""
        )

    def search(self, query: str) -> None:
        """
        Filter table by typing query into DataTables search box.

        Args:
            query: Keyword to search.
        """
        search_input = self.page.locator(f"input[aria-controls='{self.table_id}']")
        search_input.fill(query)
        self.page.wait_for_timeout(500)

    def get_row_count(self) -> int:
        """Return number of visible rows in table body."""
        return self.page.locator(f"#{self.table_id} tbody tr").count()

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
