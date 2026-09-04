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

    def get_table_body_text(self) -> str:
        """Return text content of current visible rows in the targets table."""
        return self.page.locator("#targets-table tbody").inner_text()
