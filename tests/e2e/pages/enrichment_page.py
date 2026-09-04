"""Page Object for Functional Enrichment tab and g:Profiler analysis controls."""

from tests.e2e.pages.base_page import BasePage


class EnrichmentPage(BasePage):
    """Page component for Functional Enrichment tab, scope filters, and chips."""

    ENRICH_DB_RADIO_IDS = {
        "mirtarbase": "#enrich-db-mirtarbase",
        "consensus": "#enrich-db-consensus",
        "tarbase": "#enrich-db-tarbase",
        "all": "#enrich-db-all",
    }

    def navigate_to_enrichment(self) -> None:
        """Switch to Functional Enrichment tab."""
        self.switch_tab("enrichment")
        self.page.wait_for_timeout(500)

    def select_database(self, db_name: str) -> None:
        """
        Select database source on the enrichment tab.

        Args:
            db_name: One of 'mirtarbase', 'consensus', 'tarbase', 'all'.
        """
        radio_id = self.ENRICH_DB_RADIO_IDS.get(db_name)
        if not radio_id:
            raise ValueError(f"Unknown database: {db_name}")
        label = self.page.locator(f"label[for='{radio_id.lstrip('#')}']")
        label.click()
        self.page.wait_for_timeout(400)

    def is_database_selected(self, db_name: str) -> bool:
        """Check if a database source radio is currently selected."""
        radio_id = self.ENRICH_DB_RADIO_IDS.get(db_name)
        if not radio_id:
            return False
        return self.page.locator(radio_id).is_checked()

    def is_database_button_disabled(self, db_name: str) -> bool:
        """Check if a database radio input is disabled."""
        radio_id = self.ENRICH_DB_RADIO_IDS.get(db_name)
        if not radio_id:
            return True
        return self.page.locator(radio_id).is_disabled()

    def is_awaiting_selection_prompt_visible(self) -> bool:
        """Check if the empty/step 1 guide prompt is displayed."""
        chips_box = self.page.locator("#enrichment-gene-chips")
        return "Step 1: Select miRNAs" in chips_box.inner_text()

    def get_chips_content(self) -> str:
        """Return text content of the target gene chips area."""
        return self.page.locator("#enrichment-gene-chips").inner_text().strip()

    def get_run_button_text(self) -> str:
        """Return label text of the Run Enrichment CTA button."""
        return self.page.locator("#btn-run-enrichment").inner_text().strip()

    def is_run_button_enabled(self) -> bool:
        """Check if the Run Enrichment CTA button is active/clickable."""
        btn = self.page.locator("#btn-run-enrichment")
        return not btn.is_disabled() and "disabled" not in (
            btn.get_attribute("class") or ""
        )
