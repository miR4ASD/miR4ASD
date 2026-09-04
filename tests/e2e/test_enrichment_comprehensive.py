"""Comprehensive E2E tests for Functional Enrichment workflow and results."""

import json

from playwright.sync_api import Page, Route

from tests.e2e.pages.enrichment_page import EnrichmentPage
from tests.e2e.pages.expression_page import ExpressionPage


def test_enrichment_target_scope_switching(app_page: Page, base_url: str):
    """Verify switching target scope radios updates gene scope and badges."""
    expr_page = ExpressionPage(app_page, base_url)
    enrichment_page = EnrichmentPage(app_page, base_url)

    # Select miRNA in Expression Studies
    expr_page.navigate_to_expression()
    expr_page.select_row_by_index(0)

    # Navigate to Functional Enrichment
    enrichment_page.navigate_to_enrichment()

    # Scope: All Targets (default)
    assert enrichment_page.is_scope_selected("all")

    # Scope: Strong Evidence
    enrichment_page.select_target_scope("strong")
    assert enrichment_page.is_scope_selected("strong")

    # Scope: SFARI Genes
    enrichment_page.select_target_scope("sfari")
    assert enrichment_page.is_scope_selected("sfari")

    # Scope: SFARI Category 1
    enrichment_page.select_target_scope("sfari-cat1")
    assert enrichment_page.is_scope_selected("sfari-cat1")

    # Scope: Brain Expressed
    enrichment_page.select_target_scope("brain")
    assert enrichment_page.is_scope_selected("brain")

    # Return to All
    enrichment_page.select_target_scope("all")
    assert enrichment_page.is_scope_selected("all")


def test_enrichment_custom_gene_editor(app_page: Page, base_url: str):
    """Verify custom gene editor collapsible box, typing genes, and clear button."""
    enrichment_page = EnrichmentPage(app_page, base_url)
    enrichment_page.navigate_to_enrichment()

    # Expand gene editor
    enrichment_page.toggle_gene_editor()

    # Type custom ASD genes
    custom_genes = "PTEN, SHANK3, MECP2, CHD8, SCN2A"
    enrichment_page.set_custom_genes(custom_genes)

    # CTA button should now be enabled with gene count
    assert enrichment_page.is_run_button_enabled()
    assert "5" in enrichment_page.get_run_button_text()

    # Test copy button
    enrichment_page.click_copy_genes()

    # Click clear button
    enrichment_page.click_clear_genes()
    assert not enrichment_page.is_run_button_enabled()


def test_enrichment_advanced_settings_and_parameters(app_page: Page, base_url: str):
    """Verify toggling advanced ontology sources and significance thresholds."""
    enrichment_page = EnrichmentPage(app_page, base_url)
    enrichment_page.navigate_to_enrichment()

    # Expand advanced settings
    enrichment_page.toggle_advanced_settings()

    # Toggle ontologies
    enrichment_page.toggle_ontology("wp", True)
    enrichment_page.toggle_ontology("kegg", False)

    # Change multiple testing method and threshold
    enrichment_page.set_threshold("bonferroni", "0.01")


def test_enrichment_execution_and_results_dashboard_mocked(
    app_page: Page, base_url: str
):
    """Verify full enrichment analysis execution, metrics ribbon, chart, and table."""
    enrichment_page = EnrichmentPage(app_page, base_url)

    # Mock g:Profiler REST API
    mock_payload = {
        "result": [
            {
                "source": "GO:BP",
                "native": "GO:0007268",
                "name": "chemical synaptic transmission",
                "p_value": 0.00012,
                "significant": True,
                "description": "The process by which signal is passed across synapse.",
                "term_size": 450,
                "query_size": 5,
                "intersection_size": 3,
                "effective_domain_size": 18000,
                "precision": 0.6,
                "recall": 0.006,
                "intersections": [["PTEN"], ["SHANK3"], ["MECP2"]],
            },
            {
                "source": "KEGG",
                "native": "KEGG:04724",
                "name": "Glutamatergic synapse",
                "p_value": 0.00085,
                "significant": True,
                "description": "Glutamatergic synapse pathway.",
                "term_size": 210,
                "query_size": 5,
                "intersection_size": 2,
                "effective_domain_size": 18000,
                "precision": 0.4,
                "recall": 0.009,
                "intersections": [["SHANK3"], ["SCN2A"]],
            },
        ]
    }

    def handle_gprofiler_route(route: Route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_payload),
        )

    app_page.route("**/gprofiler/api/gost/profile/**", handle_gprofiler_route)

    enrichment_page.navigate_to_enrichment()
    enrichment_page.toggle_gene_editor()
    enrichment_page.set_custom_genes("PTEN, SHANK3, MECP2, CHD8, SCN2A")

    # Run analysis
    enrichment_page.click_run_enrichment()

    # Results container should be visible
    app_page.wait_for_selector(
        "#enrichment-results-container:not(.d-none)", timeout=10000
    )
    assert enrichment_page.is_results_container_visible()

    # Verify metrics ribbon
    assert enrichment_page.get_total_terms_metric() == "2"
    assert "chemical synaptic transmission" in (
        enrichment_page.get_top_term_name_metric()
    )

    # Verify chart canvas and results table
    assert enrichment_page.is_chart_canvas_visible()
    assert enrichment_page.get_results_table_rows_count() > 0

    # Verify portal URL button
    portal_url = enrichment_page.get_gprofiler_web_button_url()
    assert "biit.cs.ut.ee/gprofiler" in portal_url


def test_enrichment_empty_results_notice(app_page: Page, base_url: str):
    """Verify warning alert is displayed when g:Profiler returns zero enriched terms."""
    enrichment_page = EnrichmentPage(app_page, base_url)

    # Mock empty g:Profiler response
    def handle_empty_route(route: Route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"result": []}),
        )

    app_page.route("**/gprofiler/api/gost/profile/**", handle_empty_route)

    enrichment_page.navigate_to_enrichment()
    enrichment_page.toggle_gene_editor()
    enrichment_page.set_custom_genes("PTEN, SHANK3")

    enrichment_page.click_run_enrichment()

    app_page.wait_for_selector("#enrichment-error:not(.d-none)", timeout=10000)
    assert enrichment_page.is_error_alert_visible()
    assert "No significantly enriched terms found" in (
        enrichment_page.get_error_alert_message()
    )


def test_enrichment_api_error_notice(app_page: Page, base_url: str):
    """Verify error alert is displayed when g:Profiler API returns HTTP error."""
    enrichment_page = EnrichmentPage(app_page, base_url)

    # Mock API server error (HTTP 500)
    def handle_error_route(route: Route):
        route.fulfill(
            status=500,
            content_type="application/json",
            body=json.dumps({"error": "Internal Server Error"}),
        )

    app_page.route("**/gprofiler/api/gost/profile/**", handle_error_route)

    enrichment_page.navigate_to_enrichment()
    enrichment_page.toggle_gene_editor()
    enrichment_page.set_custom_genes("PTEN, SHANK3")

    enrichment_page.click_run_enrichment()

    app_page.wait_for_selector("#enrichment-error:not(.d-none)", timeout=10000)
    assert enrichment_page.is_error_alert_visible()
    assert "error" in enrichment_page.get_error_alert_message().lower()


def test_enrichment_database_switcher_updates_target_gene_count(
    app_page: Page, base_url: str
):
    """Verify switching database source updates target gene counts dynamically."""
    expr_page = ExpressionPage(app_page, base_url)
    enrichment_page = EnrichmentPage(app_page, base_url)

    # Select first miRNA (hsa-let-7a-5p) in Expression Studies
    expr_page.navigate_to_expression()
    expr_page.select_row_by_index(0)

    # Navigate to Functional Enrichment
    enrichment_page.navigate_to_enrichment()

    # 1. miRTarBase (default): 78 target genes
    assert enrichment_page.is_database_selected("mirtarbase")
    stats_mirtarbase = enrichment_page.get_gene_set_stats_text()
    assert "78" in stats_mirtarbase
    assert enrichment_page.get_chips_count() == 78
    assert "78" in enrichment_page.get_run_button_text()

    # 2. Consensus: 73 target genes
    enrichment_page.select_database("consensus")
    assert enrichment_page.is_database_selected("consensus")
    stats_consensus = enrichment_page.get_gene_set_stats_text()
    assert "73" in stats_consensus
    assert enrichment_page.get_chips_count() == 73
    assert "73" in enrichment_page.get_run_button_text()

    # 3. TarBase: 792 target genes
    enrichment_page.select_database("tarbase")
    assert enrichment_page.is_database_selected("tarbase")
    stats_tarbase = enrichment_page.get_gene_set_stats_text()
    assert "792" in stats_tarbase
    assert enrichment_page.get_chips_count() == 792
    assert "792" in enrichment_page.get_run_button_text()

    # 4. All Sources (Union): 797 target genes
    enrichment_page.select_database("all")
    assert enrichment_page.is_database_selected("all")
    stats_all = enrichment_page.get_gene_set_stats_text()
    assert "797" in stats_all
    assert enrichment_page.get_chips_count() == 797
    assert "797" in enrichment_page.get_run_button_text()

    # 5. Return to miRTarBase: 78 target genes
    enrichment_page.select_database("mirtarbase")
    assert enrichment_page.is_database_selected("mirtarbase")
    assert "78" in enrichment_page.get_gene_set_stats_text()
    assert enrichment_page.get_chips_count() == 78
