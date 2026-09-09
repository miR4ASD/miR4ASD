"""Page Object for Target Genes table, single-source DB badge, and inline filters."""

import re

from tests.e2e.pages.base_page import BasePage


class TargetsPage(BasePage):
    """Page component for the Target Genes tab, DB badge, and per-tab filters."""

    DB_BADGE_ID = "#active-db-label"
    # Inline per-tab filter selectors (Target Genes Filters card)
    FILTER_GENE = "#filter-target-gene"
    FILTER_SFARI = "#filter-sfari-category"
    FILTER_EVIDENCE = "#filter-evidence-level"
    FILTER_METHOD = "#filter-target-method"
    FILTER_REGULATION = "#filter-target-regulation"
    FILTER_TISSUE = "#filter-target-tissue"

    def navigate_to_targets(self) -> None:
        """Switch to Target Genes tab and wait for DataTables to render."""
        self.switch_tab("targets")
        self.page.wait_for_selector("#targets-table tbody tr", timeout=15000)

    def get_database_badge_text(self) -> str:
        """Return the single-source database badge text (e.g. 'miRTarBase 10.0')."""
        return self.page.locator(self.DB_BADGE_ID).inner_text().strip()

    def is_single_source_mirtarbase(self) -> bool:
        """Check that the badge reflects the sole miRTarBase 10.0 source."""
        return "miRTarBase" in self.get_database_badge_text()

    def get_active_count_text(self) -> str:
        """Return the text of the active interaction count badge."""
        badge = self.page.locator("#db-active-count")
        return badge.inner_text().strip()

    def get_active_genes_count_text(self) -> str:
        """Return the text of the active unique target gene count badge."""
        badge = self.page.locator("#db-active-genes-count")
        return badge.inner_text().strip()

    def get_filtered_total(self) -> int:
        """
        Return the total post-filter interaction count.

        Parses the active interaction count badge (``#db-active-count``), which
        reflects the full filtered dataset rather than the visible page.
        """
        digits = re.sub(r"\D", "", self.get_active_count_text())
        return int(digits) if digits else 0



    def get_table_body_text(self) -> str:
        """Return text content of current visible rows in the targets table."""
        return self.page.locator("#targets-table tbody").inner_text()

    def search(self, query: str) -> None:
        """
        Filter targets table by gene symbol via the inline Target Gene filter.

        Args:
            query: One or more newline/comma separated gene symbols ('' to clear).
        """
        self.fill_filter_input(self.FILTER_GENE, query)
        self.page.wait_for_timeout(300)

    def select_sfari_category(self, value: str) -> None:
        """Select an SFARI category option ('' for All Target Genes)."""
        self.select_filter_option(self.FILTER_SFARI, value)

    def select_evidence_level(self, value: str) -> None:
        """Select an evidence level option ('' for All)."""
        self.select_filter_option(self.FILTER_EVIDENCE, value)

    def select_method(self, value: str) -> None:
        """Select an experimental technique option ('' for All)."""
        self.select_filter_option(self.FILTER_METHOD, value)

    def select_regulation(self, value: str) -> None:
        """Select a target regulation option ('' for All)."""
        self.select_filter_option(self.FILTER_REGULATION, value)

    def filter_tissue(self, value: str) -> None:
        """Set the tissue / cell source filter ('' to clear)."""
        self.fill_filter_input(self.FILTER_TISSUE, value)

    def reset_target_filters(self) -> None:
        """Click the per-tab 'Clear All' (targets scope) filter reset button."""
        sel = '#targets .btn-clear-all-chips[data-reset-scope="targets"]'
        self.page.locator(sel).click()
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
