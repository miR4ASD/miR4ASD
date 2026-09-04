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

    def get_chips_count(self) -> int:
        """Return count of individual gene chip badges currently rendered."""
        return self.page.locator("#enrichment-gene-chips span.gene-chip").count()

    def get_gene_set_stats_text(self) -> str:
        """Return summary stats text (e.g. '78 / 797 Target Genes')."""
        return self.page.locator("#gene-set-stats").inner_text().strip()

    def get_run_button_text(self) -> str:
        """Return label text of the Run Enrichment CTA button."""
        return self.page.locator("#btn-run-enrichment").inner_text().strip()

    def is_run_button_enabled(self) -> bool:
        """Check if the Run Enrichment CTA button is active/clickable."""
        btn = self.page.locator("#btn-run-enrichment")
        return not btn.is_disabled() and "disabled" not in (
            btn.get_attribute("class") or ""
        )

    def select_target_scope(self, scope: str) -> None:
        """
        Select a target gene scope radio button.

        Args:
            scope: One of 'all', 'strong', 'sfari', 'sfari-cat1', 'brain',
                   'upregulated', 'downregulated'.
        """
        label = self.page.locator(f"label[for='scope-{scope}']")
        label.click()
        self.page.wait_for_timeout(400)

    def is_scope_selected(self, scope: str) -> bool:
        """Check if target scope radio is selected."""
        return self.page.locator(f"#scope-{scope}").is_checked()

    def toggle_gene_editor(self) -> None:
        """Toggle collapsible custom gene editor textarea."""
        self.page.locator("[data-bs-target='#geneEditorCollapse']").click()
        self.page.wait_for_timeout(400)

    def set_custom_genes(self, genes_text: str) -> None:
        """
        Type custom gene symbols into gene editor textarea.

        Args:
            genes_text: Space/comma/line separated gene symbols.
        """
        textarea = self.page.locator("#enrichment-gene-input")
        textarea.fill(genes_text)
        textarea.dispatch_event("input")
        self.page.wait_for_timeout(400)

    def click_clear_genes(self) -> None:
        """Click Clear button in gene editor header."""
        self.page.locator("#btn-clear-genes").click()
        self.page.wait_for_timeout(400)

    def click_copy_genes(self) -> None:
        """Click Copy button in gene editor header."""
        self.page.locator("#btn-copy-genes").click()
        self.page.wait_for_timeout(300)

    def toggle_advanced_settings(self) -> None:
        """Toggle collapsible advanced ontologies and parameters settings."""
        self.page.locator("[data-bs-target='#advancedSettingsCollapse']").click()
        self.page.wait_for_timeout(400)

    def toggle_ontology(self, source_code: str, enable: bool) -> None:
        """
        Enable or disable a specific ontology source checkbox.

        Args:
            source_code: One of 'gobp', 'gomf', 'gocc', 'kegg', 'reac', 'hp', 'wp'.
            enable: True to check, False to uncheck.
        """
        cb = self.page.locator(f"#src-{source_code.lower()}")
        if cb.is_checked() != enable:
            cb.click()
            self.page.wait_for_timeout(300)

    def set_threshold(self, method: str, value: str) -> None:
        """
        Set significance testing method and threshold.

        Args:
            method: 'g_SCS', 'fdr', or 'bonferroni'.
            value: '0.01', '0.05', or '0.10'.
        """
        self.page.locator("#threshold-method").select_option(method)
        self.page.locator("#threshold-value").select_option(value)
        self.page.wait_for_timeout(300)

    def click_run_enrichment(self) -> None:
        """Click Run g:Profiler Functional Enrichment button."""
        self.page.locator("#btn-run-enrichment").click()

    def is_loading_spinner_visible(self) -> bool:
        """Check if querying g:Profiler loading spinner is visible."""
        spinner = self.page.locator("#enrichment-loading")
        return spinner.is_visible() and "d-none" not in (
            spinner.get_attribute("class") or ""
        )

    def is_results_container_visible(self) -> bool:
        """Check if enrichment results container is visible."""
        container = self.page.locator("#enrichment-results-container")
        return container.is_visible() and "d-none" not in (
            container.get_attribute("class") or ""
        )

    def is_error_alert_visible(self) -> bool:
        """Check if error/notice alert is visible."""
        alert = self.page.locator("#enrichment-error")
        return alert.is_visible() and "d-none" not in (
            alert.get_attribute("class") or ""
        )

    def get_error_alert_message(self) -> str:
        """Return text of error/notice alert."""
        return self.page.locator("#enrichment-error-msg").inner_text().strip()

    def get_total_terms_metric(self) -> str:
        """Return Enriched Terms metric value."""
        return self.page.locator("#res-total-terms").inner_text().strip()

    def get_top_source_metric(self) -> str:
        """Return Top Pathway Source metric value."""
        return self.page.locator("#res-top-source").inner_text().strip()

    def get_top_term_name_metric(self) -> str:
        """Return Most Significant Term metric value."""
        return self.page.locator("#res-top-term-name").inner_text().strip()

    def get_sfari_covered_metric(self) -> str:
        """Return SFARI Genes Covered metric value."""
        return self.page.locator("#res-sfari-covered").inner_text().strip()

    def is_chart_canvas_visible(self) -> bool:
        """Check if Top 15 pathways chart canvas is rendered."""
        return self.page.locator("#enrichmentChart").is_visible()

    def click_download_chart_png(self) -> None:
        """Click Download Chart PNG button."""
        self.page.locator("#btn-export-enrichment-chart").click()

    def click_download_csv(self) -> None:
        """Click Download CSV button."""
        self.page.locator("#btn-export-enrichment-csv").click()

    def get_gprofiler_web_button_url(self) -> str:
        """Return target URL for Open in g:Profiler Web Portal button."""
        return self.page.locator("#btn-open-gprofiler-web").get_attribute("href") or ""

    def get_results_table_rows_count(self) -> int:
        """Return row count of results DataTable."""
        return self.page.locator("#enrichment-results-table tbody tr").count()
