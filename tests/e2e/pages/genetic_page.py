"""Page Object for Genetic & Other Studies tab and selection controls."""

from playwright.sync_api import Page

from tests.e2e.pages.studies_table_page import StudiesTablePage


class GeneticPage(StudiesTablePage):
    """Page component for Genetic & Other Studies table and selection controls."""

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
            select_all_class=".select-all-other",
            container_id="#genetic",
            data_table_attr="genetic",
        )

    def navigate_to_genetic(self) -> None:
        """Switch to Genetic & Other Studies tab and wait for row rendering."""
        self.navigate_table()

    # Inline per-tab filter selectors (Genetic & Other Studies Filters card)
    FILTER_MATURE = "#gen-filter-mature-id"
    FILTER_HAIRPIN = "#gen-filter-mirna-id"
    FILTER_ALTERATION = "#filter-genetic-alteration"
    FILTER_STUDY_DESC = "#filter-study-desc"

    def filter_mature(self, text: str) -> None:
        """Set the genetic miRNA mature ID filter ('' to clear)."""
        self.fill_filter_input(self.FILTER_MATURE, text)

    def filter_hairpin(self, text: str) -> None:
        """Set the genetic miRNA precursor/hairpin ID filter ('' to clear)."""
        self.fill_filter_input(self.FILTER_HAIRPIN, text)

    def select_genetic_alteration(self, value: str) -> None:
        """Select genetic alteration option ('' for All, 'CNV', 'SNV', 'SNP')."""
        self.select_filter_option(self.FILTER_ALTERATION, value)

    def filter_study_desc(self, text: str) -> None:
        """Set the study description keyword filter ('' to clear)."""
        self.fill_filter_input(self.FILTER_STUDY_DESC, text)

    def get_active_indicator_text(self) -> str:
        """Return the per-tab active filter indicator badge text."""
        return self.page.locator(".gen-active-filter-indicator").inner_text().strip()

    def get_active_chips_count(self) -> int:
        """Return the number of active filter chips rendered for this tab."""
        return self.page.locator(".gen-active-chips .filter-chip").count()
