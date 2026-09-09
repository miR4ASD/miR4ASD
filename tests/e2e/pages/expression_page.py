"""Page Object for Expression Studies tab and miRNA selection controls."""

from playwright.sync_api import Page

from tests.e2e.pages.studies_table_page import StudiesTablePage


class ExpressionPage(StudiesTablePage):
    """Page component for Expression Studies table and selection controls."""

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
            select_all_class=".select-all-expr",
            container_id="#expression",
            data_table_attr="expression",
        )

    def navigate_to_expression(self) -> None:
        """Switch to Expression Studies tab and wait for row rendering."""
        self.navigate_table()

    # Inline per-tab filter selectors (Expression Studies Filters card)
    FILTER_MATURE = "#filter-mature-id"
    FILTER_HAIRPIN = "#filter-mirna-id"
    FILTER_CHANGE = "#filter-expression-change"
    FILTER_EVIDENCE = "#filter-overall-evidence"
    TISSUE_CHECKBOXES = "#tissue-checkboxes"

    def filter_mature(self, text: str) -> None:
        """Set the miRNA mature ID filter ('' to clear)."""
        self.fill_filter_input(self.FILTER_MATURE, text)

    def filter_hairpin(self, text: str) -> None:
        """Set the miRNA precursor/hairpin ID filter ('' to clear)."""
        self.fill_filter_input(self.FILTER_HAIRPIN, text)

    def select_expression_change(self, value: str) -> None:
        """Select expression change ('' for All, Up/Downregulated)."""
        self.select_filter_option(self.FILTER_CHANGE, value)

    def select_overall_evidence(self, value: str) -> None:
        """Select overall evidence option ('' for All)."""
        self.select_filter_option(self.FILTER_EVIDENCE, value)

    def get_active_indicator_text(self) -> str:
        """Return the per-tab active filter indicator badge text."""
        return self.page.locator(".expr-active-filter-indicator").inner_text().strip()

    def get_active_chips_count(self) -> int:
        """Return the number of active filter chips rendered for this tab."""
        return self.page.locator(".expr-active-chips .filter-chip").count()

    def reset_expression_filters(self) -> None:
        """Click the per-tab 'Clear All' (expression scope) filter reset button."""
        sel = '#expression .btn-clear-all-chips[data-reset-scope="expression"]'
        self.page.locator(sel).click()
        self.page.wait_for_timeout(500)
