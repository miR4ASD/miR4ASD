"""Page Object for Expression Studies tab and miRNA selection controls."""

from playwright.sync_api import Page

from tests.e2e.pages.studies_table_page import StudiesTablePage


class ExpressionPage(StudiesTablePage):
    """Page component for Expression Studies table and selection stepper."""

    def __init__(self, page: Page, base_url: str):
        """
        Initialize the ExpressionPage object.

        Args:
            page: Playwright Page instance.
            base_url: Base application URL.
        """
        super().__init__(
            page=page,
            base_url=base_url,
            tab_name="expression",
            table_id="expression-table",
            row_check_class="expr-row-check",
            badge_class=".expr-selected-count",
            select_all_class=".select-all-expr",
            container_id="#expression",
            data_table_attr="expression",
        )

    def navigate_to_expression(self) -> None:
        """Switch to Expression Studies tab and wait for row rendering."""
        self.navigate_table()
