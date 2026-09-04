"""Page Object for Target Genes table and Database Switcher controls."""

from tests.e2e.pages.base_page import BasePage


class TargetsPage(BasePage):
    """Page component for Target Genes tab, database source switcher, and filters."""

    DB_RADIO_IDS = {
        "mirtarbase": "#db-mirtarbase",
        "consensus": "#db-consensus",
        "tarbase": "#db-tarbase",
        "all": "#db-all",
    }

    def navigate_to_targets(self) -> None:
        """Switch to Target Genes tab and wait for DataTables to render."""
        self.switch_tab("targets")
        self.page.wait_for_selector("#targets-table tbody tr", timeout=15000)

    def select_database(self, db_name: str) -> None:
        """
        Select a target interaction database source.

        Args:
            db_name: One of 'mirtarbase', 'consensus', 'tarbase', 'all'.
        """
        radio_id = self.DB_RADIO_IDS.get(db_name)
        if not radio_id:
            raise ValueError(f"Unknown database name: {db_name}")
        # Click the associated label to toggle btn-check
        label = self.page.locator(f"label[for='{radio_id.lstrip('#')}']")
        label.click()
        self.page.wait_for_timeout(600)

    def is_database_selected(self, db_name: str) -> bool:
        """Check if a specific database radio is selected."""
        radio_id = self.DB_RADIO_IDS.get(db_name)
        if not radio_id:
            return False
        return self.page.locator(radio_id).is_checked()

    def get_active_count_text(self) -> str:
        """Return the text of the active interaction count badge."""
        badge = self.page.locator("#db-active-count")
        return badge.inner_text().strip()

    def get_active_genes_count_text(self) -> str:
        """Return the text of the active unique target gene count badge."""
        badge = self.page.locator("#db-active-genes-count")
        return badge.inner_text().strip()

    def get_table_body_text(self) -> str:
        """Return text content of current visible rows in the targets table."""
        return self.page.locator("#targets-table tbody").inner_text()

    def search(self, query: str) -> None:
        """
        Filter targets table by query in DataTables search box.

        Args:
            query: Keyword or gene symbol to search.
        """
        search_input = self.page.locator("input[aria-controls='targets-table']")
        search_input.fill(query)
        self.page.wait_for_timeout(500)

    def get_row_count(self) -> int:
        """Return count of visible rows in target genes table."""
        return self.page.locator("#targets-table tbody tr").count()

    def expand_row_details(self, index: int = 0) -> None:
        """
        Click child details toggle on target gene row by index.

        Args:
            index: 0-based row index.
        """
        control = self.page.locator("#targets-table tbody tr td.details-control").nth(
            index
        )
        control.click()
        self.page.wait_for_timeout(400)

    def is_child_row_visible(self) -> bool:
        """Check if any expandable child row details card is visible."""
        return self.page.locator(
            "#targets-table tbody tr.details, #targets-table tbody tr.dt-hasChild"
        ).is_visible()

    def get_child_row_text(self) -> str:
        """Return text inside visible child row details."""
        child = self.page.locator(
            "#targets-table tbody tr.child, #targets-table tbody tr.details + tr"
        ).first
        if child.is_visible():
            return child.inner_text()
        return ""

    def is_analyze_button_enabled(self) -> bool:
        """Check if target enrichment button is enabled."""
        btn = self.page.locator(".btn-analyze-filtered[data-source-table='targets']")
        return not btn.is_disabled() and "disabled" not in (
            btn.get_attribute("class") or ""
        )

    def get_analyze_button_text(self) -> str:
        """Return text of the target enrichment button."""
        return (
            self.page.locator(".btn-analyze-filtered[data-source-table='targets']")
            .inner_text()
            .strip()
        )

    def click_page(self, page_num: int) -> None:
        """
        Navigate to specific page in DataTables pagination.

        Args:
            page_num: Page number (1-indexed).
        """
        btn = self.page.locator(
            f"button.dt-paging-button[aria-controls='targets-table']"
            f":text-is('{page_num}'), "
            f"#targets-tab-pane button.dt-paging-button:text-is('{page_num}'), "
            f"#targets-table_paginate .paginate_button:text-is('{page_num}')"
        ).first
        btn.click()
        self.page.wait_for_timeout(500)
