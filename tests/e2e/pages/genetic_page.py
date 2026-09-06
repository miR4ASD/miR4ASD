"""Page Object for Genetic & Other Studies tab and selection controls."""

from playwright.sync_api import Page

from tests.e2e.pages.studies_table_page import StudiesTablePage


class GeneticPage(StudiesTablePage):
    """Page component for Genetic & Other Studies table and selection stepper."""

    def __init__(self, page: Page, base_url: str):
        """
        Initialize the GeneticPage object.

        Args:
            page: Playwright Page instance.
            base_url: Base application URL.
        """
        super().__init__(
            page=page,
            base_url=base_url,
            tab_name="genetic",
            table_id="other-table",
            row_check_class="gen-row-check",
            badge_class=".gen-selected-count",
            select_all_class=".select-all-other",
            container_id="#genetic",
            data_table_attr="genetic",
        )

    def navigate_to_genetic(self) -> None:
        """Switch to Genetic & Other Studies tab and wait for row rendering."""
        self.navigate_table()
