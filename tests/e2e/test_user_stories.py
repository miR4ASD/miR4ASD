"""
End-to-end user story test suite covering complete miR4ASD platform functionality.

Each test corresponds to a validated User Story (US-01 through US-08), verifying
real-world researcher workflows across discovery, filtering, functional enrichment,
interactive data dictionaries, responsive layouts, and accessibility.
"""

import json
from typing import Dict, List

from playwright.sync_api import Page, Route

from tests.e2e.pages.base_page import BasePage
from tests.e2e.pages.drawer_page import DrawerPage
from tests.e2e.pages.enrichment_page import EnrichmentPage
from tests.e2e.pages.expression_page import ExpressionPage
from tests.e2e.pages.figures_page import FiguresPage
from tests.e2e.pages.genetic_page import GeneticPage
from tests.e2e.pages.targets_page import TargetsPage

MOCK_GPROFILER_PAYLOAD: Dict = {
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


def test_user_story_1_expression_discovery_and_selection(
    app_page: Page, base_url: str
) -> None:
    """
    US-01: Expression Studies discovery, citation inspection, and batch selection.

    Validates that researchers can search expression profiling studies, inspect
    child-row PubMed metadata and DOIs, toggle visible rows, and activate the
    enrichment CTA button.
    """
    expr_page = ExpressionPage(app_page, base_url)
    expr_page.navigate_to_expression()

    # Initial state: 0 selected and analyze CTA disabled
    assert expr_page.get_selected_count() == "0"
    assert not expr_page.is_run_enrichment_button_enabled()

    # Search for specific candidate miRNA (miR-132)
    initial_count = expr_page.get_row_count()
    expr_page.search("miR-132")
    filtered_count = expr_page.get_row_count()
    assert 0 < filtered_count <= initial_count

    # Expand child row details to verify literature citation and DOI links
    expr_page.expand_row_details(0)
    assert expr_page.is_child_row_visible()
    child_text = expr_page.get_child_row_text().lower()
    assert len(child_text) > 0 and ("study" in child_text or "samples" in child_text)

    # Collapse details and reset search
    expr_page.expand_row_details(0)
    assert not expr_page.is_child_row_visible()
    expr_page.search("")
    assert expr_page.get_row_count() == initial_count

    # Select visible rows and verify enrichment stepper CTA enablement
    expr_page.click_select_visible()
    selected_count = expr_page.get_selected_count()
    assert int(selected_count) > 0
    assert expr_page.is_run_enrichment_button_enabled()

    # Clear selection and verify disabled CTA
    expr_page.click_clear_selection()
    assert expr_page.get_selected_count() == "0"
    assert not expr_page.is_run_enrichment_button_enabled()

    # Test master header checkbox toggle
    expr_page.click_header_select_all()
    assert expr_page.is_header_select_all_checked()
    assert int(expr_page.get_selected_count()) > 0
    expr_page.click_header_select_all()
    assert not expr_page.is_header_select_all_checked()
    assert expr_page.get_selected_count() == "0"


def test_user_story_2_genetic_studies_cross_selection(
    app_page: Page, base_url: str
) -> None:
    """
    US-02: Genetic alterations filtering, methodology details, and cross-study tally.

    Validates that geneticists can filter alteration types, inspect genomic coordinates
    and validation methodology in expandable child rows, and aggregate candidate
    alterations across multiple pagination pages.
    """
    genetic_page = GeneticPage(app_page, base_url)
    genetic_page.navigate_to_genetic()

    # Initial state
    assert genetic_page.get_selected_count() == "0"
    initial_rows = genetic_page.get_row_count()
    assert initial_rows > 0

    # Search for specific alteration type (e.g. SNV)
    genetic_page.search("SNV")
    filtered_rows = genetic_page.get_row_count()
    assert 0 < filtered_rows <= initial_rows

    # Expand child row details to verify genomic coordinates / methodology
    genetic_page.expand_row_details(0)
    assert genetic_page.is_child_row_visible()
    child_text = genetic_page.get_child_row_text()
    assert len(child_text) > 0
    genetic_page.expand_row_details(0)

    # Clear search
    genetic_page.search("")
    assert genetic_page.get_row_count() == initial_rows

    # Select row on page 1
    genetic_page.select_row_by_index(0)
    count_p1 = int(genetic_page.get_selected_count())
    assert count_p1 == 1

    # Navigate to page 2 and select an additional row
    genetic_page.click_page(2)
    genetic_page.select_row_by_index(0)
    count_p2 = int(genetic_page.get_selected_count())
    assert count_p2 >= 2

    # Clear selection
    genetic_page.click_clear_selection()
    assert genetic_page.get_selected_count() == "0"


def test_user_story_3_target_genes_provenance_and_details(
    app_page: Page, base_url: str
) -> None:
    """
    US-03: Validated target genes exploration, database switcher, and assays.

    Validates switching between miRTarBase, Consensus, TarBase, and All Sources,
    confirming accurate interaction and unique gene tallies, searching for ASD targets,
    and verifying experimental assay provenance.
    """
    targets_page = TargetsPage(app_page, base_url)
    targets_page.navigate_to_targets()

    # 1. miRTarBase (default): 17,150 interactions / 2,995 unique genes
    assert targets_page.is_database_selected("mirtarbase")
    assert "17,150" in targets_page.get_active_count_text()
    assert "2,995" in targets_page.get_active_genes_count_text()

    # 2. Consensus: 7,492 interactions / 2,130 unique genes
    targets_page.select_database("consensus")
    assert targets_page.is_database_selected("consensus")
    assert "7,492" in targets_page.get_active_count_text()
    assert "2,130" in targets_page.get_active_genes_count_text()

    # 3. TarBase: 68,495 interactions / 2,577 unique genes
    targets_page.select_database("tarbase")
    assert targets_page.is_database_selected("tarbase")
    assert "68,495" in targets_page.get_active_count_text()
    assert "2,577" in targets_page.get_active_genes_count_text()

    # 4. All Sources: 78,153 interactions / 3,281 unique genes
    targets_page.select_database("all")
    assert targets_page.is_database_selected("all")
    assert "78,153" in targets_page.get_active_count_text()
    assert "3,281" in targets_page.get_active_genes_count_text()

    # Return to miRTarBase and search for ASD target PTEN
    targets_page.select_database("mirtarbase")
    targets_page.search("PTEN")
    assert targets_page.get_row_count() > 0
    assert "PTEN" in targets_page.get_table_body_text()

    # Expand child row details to verify experimental methods and regulatory effect
    targets_page.expand_row_details(0)
    assert targets_page.is_child_row_visible()
    child_text = targets_page.get_child_row_text()
    assert len(child_text) > 0
    targets_page.expand_row_details(0)
    targets_page.search("")


def test_user_story_4_end_to_end_enrichment_pipeline(
    app_page: Page, base_url: str
) -> None:
    """
    US-04: End-to-end functional enrichment workflow from miRNA selection to reports.

    Validates candidate selection in Expression Studies, derivation in Functional
    Enrichment, real-time database and scope switching, mocked g:Profiler execution,
    metrics ribbon, chart canvas, results table, and export capabilities.
    """
    expr_page = ExpressionPage(app_page, base_url)
    enrichment_page = EnrichmentPage(app_page, base_url)

    # Mock g:Profiler API
    def handle_gprofiler_route(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(MOCK_GPROFILER_PAYLOAD),
        )

    app_page.route("**/gprofiler/api/gost/profile/**", handle_gprofiler_route)

    # 1. Select miRNA (hsa-let-7a-5p) in Expression Studies
    expr_page.navigate_to_expression()
    expr_page.select_row_by_index(0)

    # 2. Trigger Run Functional Enrichment CTA
    expr_page.click_run_enrichment()
    assert enrichment_page.is_tab_active("enrichment")

    # 3. Dynamic database switching updates gene count
    assert enrichment_page.is_database_selected("mirtarbase")
    assert "78" in enrichment_page.get_gene_set_stats_text()
    assert enrichment_page.get_chips_count() == 78

    enrichment_page.select_database("consensus")
    assert "73" in enrichment_page.get_gene_set_stats_text()
    assert enrichment_page.get_chips_count() == 73

    enrichment_page.select_database("tarbase")
    assert "792" in enrichment_page.get_gene_set_stats_text()
    assert enrichment_page.get_chips_count() == 792

    enrichment_page.select_database("mirtarbase")
    assert "78" in enrichment_page.get_gene_set_stats_text()

    # 4. Target scope switching
    enrichment_page.select_target_scope("strong")
    assert enrichment_page.is_scope_selected("strong")
    enrichment_page.select_target_scope("sfari")
    assert enrichment_page.is_scope_selected("sfari")
    enrichment_page.select_target_scope("brain")
    assert enrichment_page.is_scope_selected("brain")
    enrichment_page.select_target_scope("all")
    assert enrichment_page.is_scope_selected("all")

    # 5. Execute Enrichment Analysis
    enrichment_page.click_run_enrichment()

    # 6. Verify Results Dashboard
    app_page.wait_for_selector(
        "#enrichment-results-container:not(.d-none)", timeout=10000
    )
    assert enrichment_page.is_results_container_visible()
    assert enrichment_page.get_total_terms_metric() == "2"
    assert "chemical synaptic transmission" in (
        enrichment_page.get_top_term_name_metric()
    )
    assert enrichment_page.is_chart_canvas_visible()
    assert enrichment_page.get_results_table_rows_count() > 0

    # 7. Verify portal URL and CSV export buttons
    portal_url = enrichment_page.get_gprofiler_web_button_url()
    assert "biit.cs.ut.ee/gprofiler" in portal_url
    assert app_page.locator("#btn-export-enrichment-csv").is_visible()


def test_user_story_5_custom_gene_editor_and_parameters(
    app_page: Page, base_url: str
) -> None:
    """
    US-05: Custom gene list entry, ontology parameters, and graceful error alerts.

    Validates typing custom ASD gene symbols, clipboard copy/clear controls,
    adjusting ontologies and multiple testing correction methods, and user alerts
    for empty results and server errors.
    """
    enrichment_page = EnrichmentPage(app_page, base_url)
    enrichment_page.navigate_to_enrichment()

    # 1. Custom Gene Editor: Typing and parsing
    enrichment_page.toggle_gene_editor()
    custom_genes = "PTEN, SHANK3, MECP2, CHD8, SCN2A"
    enrichment_page.set_custom_genes(custom_genes)
    assert enrichment_page.is_run_button_enabled()
    assert "5" in enrichment_page.get_run_button_text()

    # 2. Copy and Clear controls
    enrichment_page.click_copy_genes()
    enrichment_page.click_clear_genes()
    assert not enrichment_page.is_run_button_enabled()

    # Re-enter genes for parameter testing
    enrichment_page.set_custom_genes("PTEN, SHANK3")

    # 3. Advanced Settings: Ontologies & multiple testing thresholds
    enrichment_page.toggle_advanced_settings()
    enrichment_page.toggle_ontology("wp", True)
    enrichment_page.toggle_ontology("kegg", False)
    enrichment_page.set_threshold("bonferroni", "0.01")

    # 4. Empty results alert handling
    def handle_empty_route(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"result": []}),
        )

    app_page.route("**/gprofiler/api/gost/profile/**", handle_empty_route)
    enrichment_page.click_run_enrichment()
    app_page.wait_for_selector("#enrichment-error:not(.d-none)", timeout=10000)
    assert enrichment_page.is_error_alert_visible()
    assert "No significantly enriched terms found" in (
        enrichment_page.get_error_alert_message()
    )

    # 5. Server error alert handling
    def handle_error_route(route: Route) -> None:
        route.fulfill(
            status=500,
            content_type="application/json",
            body=json.dumps({"error": "Internal Server Error"}),
        )

    app_page.route("**/gprofiler/api/gost/profile/**", handle_error_route)
    enrichment_page.click_run_enrichment()
    app_page.wait_for_selector("#enrichment-error:not(.d-none)", timeout=10000)
    assert enrichment_page.is_error_alert_visible()
    assert "error" in enrichment_page.get_error_alert_message().lower()


def test_user_story_6_filter_drawer_multi_parameter_query(
    app_page: Page, base_url: str
) -> None:
    """
    US-06: Unified slide-over multi-parameter filter drawer and query formulation.

    Validates opening and closing the drawer via various methods, switching search
    mode tabs, applying categorical filters, inspecting the active criteria badge,
    and triggering enrichment from within the drawer.
    """
    expr_page = ExpressionPage(app_page, base_url)
    drawer_page = DrawerPage(app_page, base_url)
    expr_page.navigate_to_expression()
    expr_page.select_row_by_index(0)

    # Open filter drawer
    drawer_page.open_drawer()
    assert drawer_page.is_drawer_open()

    # Switch search modes and enter values
    drawer_page.set_search_mode("hairpin")
    drawer_page.enter_search_text("hairpin", "mir-132")

    drawer_page.set_search_mode("gene")
    drawer_page.enter_search_text("gene", "PTEN")

    drawer_page.set_search_mode("mature")
    drawer_page.enter_search_text("mature", "hsa-let-7a-5p")

    # Set categorical dropdown filters
    drawer_page.select_sfari_category("Category 1")
    drawer_page.select_evidence_level("Strong Evidence")
    drawer_page.select_expression_change("Upregulated")
    drawer_page.select_genetic_alteration("CNV")

    # Active filter count badge should reflect applied filters
    badge_text = drawer_page.get_filter_count_badge_text()
    assert badge_text != "" and badge_text != "0"

    # Click drawer enrichment CTA
    drawer_page.click_drawer_enrich_button()
    assert drawer_page.is_tab_active("enrichment")

    # Re-open drawer and clear all filters
    drawer_page.open_drawer()
    assert drawer_page.is_drawer_open()
    drawer_page.click_clear_all_footer()
    assert "0" in drawer_page.get_filter_count_badge_text()

    # Close via header close icon
    drawer_page.close_drawer_via_icon()
    assert not drawer_page.is_drawer_open()

    # Re-open and close via backdrop click
    drawer_page.open_drawer()
    assert drawer_page.is_drawer_open()
    drawer_page.close_drawer_via_backdrop()
    assert not drawer_page.is_drawer_open()


def test_user_story_7_data_dictionary_and_visualizations(
    app_page: Page, base_url: str
) -> None:
    """
    US-07: Data Dictionary table specifications and publication figures gallery.

    Validates the 5 Table Specifications badge, accordion expansion with aligned
    schema definitions, and publication figure card loading with positive dimensions.
    """
    figures_page = FiguresPage(app_page, base_url)
    figures_page.navigate_to_figures()

    # 1. Verify 5 Table Specifications badge
    badge = app_page.locator("span:has-text('Table Specifications')").first
    assert "5 Table Specifications" in badge.inner_text()

    # 2. Verify all 5 accordion specification items expand and contain exact headers
    expected_spec_headers: List[List[str]] = [
        ["Number of studies (Upregulated)", "Number of studies (Downregulated)"],
        ["Alteration", "Study description"],
        ["ASD Susceptibility (SFARI)", "PubMed Reference"],
        ["Tissue Type", "Tissue Subtype", "ASD Samples", "Control Samples"],
        ["Term ID", "Term Name", "Adjusted P-Value", "Overlap (k/N)", "Term Size"],
    ]

    accordion_buttons = app_page.locator("#dictionaryAccordion .accordion-button")
    assert accordion_buttons.count() == 5

    for idx, expected_headers in enumerate(expected_spec_headers):
        btn = accordion_buttons.nth(idx)
        btn.scroll_into_view_if_needed()
        if btn.get_attribute("aria-expanded") != "true":
            btn.click()
            app_page.wait_for_timeout(300)

        collapse = app_page.locator("#dictionaryAccordion .accordion-collapse").nth(idx)
        assert collapse.is_visible()
        collapse_text = collapse.inner_text()
        for header in expected_headers:
            assert header in collapse_text, (
                f"Missing header '{header}' in accordion specification {idx + 1}"
            )

    # 3. Verify publication figure cards render with positive dimensions
    images = figures_page.get_figure_images()
    assert len(images) >= 8

    for idx, img in enumerate(images):
        src = img.get_attribute("src") or ""
        alt = img.get_attribute("alt") or f"Figure {idx + 1}"
        w, h = figures_page.get_image_natural_dimensions(img)
        assert w > 0, f"Figure '{alt}' ({src}) naturalWidth is 0"
        assert h > 0, f"Figure '{alt}' ({src}) naturalHeight is 0"
        assert img.is_visible()

    # 4. Inline figure card click (no blocking modal)
    figures_page.click_figure_card(0)
    assert not figures_page.is_modal_present_or_visible()


def test_user_story_8_responsive_accessibility_and_global_controls(
    app_page: Page, base_url: str
) -> None:
    """
    US-08: Multi-viewport responsiveness, accessible landmarks, and floating controls.

    Validates responsive layout on mobile (375x667) and desktop (1400x900) with zero
    horizontal overflow, floating Back-to-Top scroll behavior, dismissible warning
    toasts, and WCAG landmark roles.
    """
    base_page = BasePage(app_page, base_url)
    figures_page = FiguresPage(app_page, base_url)
    enrichment_page = EnrichmentPage(app_page, base_url)

    # 1. Desktop viewport: zero overflow
    app_page.set_viewport_size({"width": 1400, "height": 900})
    base_page.navigate()
    scroll_w = app_page.evaluate("() => document.documentElement.scrollWidth")
    inner_w = app_page.evaluate("() => window.innerWidth")
    assert scroll_w <= inner_w + 5

    # 2. Mobile viewport: zero overflow and stacked figures
    app_page.set_viewport_size({"width": 375, "height": 667})
    app_page.wait_for_timeout(500)
    figures_page.navigate_to_figures()
    m_scroll_w = app_page.evaluate("() => document.documentElement.scrollWidth")
    m_inner_w = app_page.evaluate("() => window.innerWidth")
    assert m_scroll_w <= m_inner_w + 5

    for img in figures_page.get_figure_images():
        box = img.bounding_box()
        assert box is not None and box["width"] <= 375

    # Return to standard desktop
    app_page.set_viewport_size({"width": 1400, "height": 900})
    base_page.navigate()

    # 3. Floating Back-to-Top button
    top_btn = app_page.locator("#btn-back-to-top")
    assert "show" not in (top_btn.get_attribute("class") or "")
    app_page.evaluate("window.scrollTo(0, 800); $(window).trigger('scroll');")
    app_page.wait_for_selector("#btn-back-to-top.show", timeout=5000)
    assert base_page.is_back_to_top_visible()
    base_page.click_back_to_top()
    app_page.wait_for_timeout(800)
    scroll_y = app_page.evaluate("window.scrollY || window.pageYOffset;")
    assert scroll_y < 100

    # 4. Warning toast alert and dismiss
    enrichment_page.navigate_to_enrichment()
    app_page.evaluate(
        "window.showSelectionWarning && "
        "window.showSelectionWarning('Target genes required for test');"
    )
    app_page.wait_for_selector("#selectionWarningToast.show", timeout=5000)
    assert "show" in (
        app_page.locator("#selectionWarningToast").get_attribute("class") or ""
    )
    enrichment_page.dismiss_toast()
    app_page.wait_for_timeout(400)
    assert "show" not in (
        app_page.locator("#selectionWarningToast").get_attribute("class") or ""
    )

    # 5. WCAG Accessibility: Landmark roles
    assert app_page.locator("nav, [role='navigation']").count() > 0
    assert app_page.locator("main, [role='main']").count() > 0
    assert app_page.locator("[role='tablist']").count() > 0
