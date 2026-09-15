"""End-to-end tests for the per-tab inline filter cards (drawer removed)."""

from playwright.sync_api import Page

from tests.e2e.pages.expression_page import ExpressionPage
from tests.e2e.pages.genetic_page import GeneticPage
from tests.e2e.pages.targets_page import TargetsPage


def test_drawer_dom_removed_and_inline_cards_present(app_page: Page, base_url: str):
    """Verify removed controls are gone and per-tab inline cards exist."""
    app_page.goto(base_url, wait_until="domcontentloaded")
    app_page.wait_for_timeout(500)

    removed_selectors = [
        "#filterDrawer",
        "#drawerBackdrop",
        ".btn-filter",
        "#resetFilters",
        "#closeFilterDrawer",
        ".workflow-stepper-card",
        ".step-pill",
        ".btn-select-all-visible",
        ".btn-clear-selection",
        ".btn-analyze-filtered[data-source-table=expression]",
        ".btn-analyze-filtered[data-source-table=genetic]",
        ".expr-selected-badge",
        ".gen-selected-badge",
    ]
    for selector in removed_selectors:
        assert app_page.locator(selector).count() == 0, (
            f"Removed drawer element still present: {selector}"
        )

    for container in ["#expression", "#genetic", "#targets"]:
        assert app_page.locator(f"{container} .filter-card-inline").count() == 1, (
            f"Missing inline filter card in {container}"
        )


def test_expression_card_filter_chips_and_reset(app_page: Page, base_url: str):
    """Verify Expression inline card filter chips, indicator, and clear-all."""
    expr_page = ExpressionPage(app_page, base_url)
    expr_page.navigate_to_expression()

    assert expr_page.get_filtered_total() == 524
    assert expr_page.get_active_indicator_text() == "No Filters Active"
    assert expr_page.get_active_chips_count() == 0

    expr_page.filter_mature("hsa-let-7a-5p")
    assert expr_page.get_filtered_total() == 6
    assert expr_page.get_active_indicator_text() == "1 Active: 1 Mature"
    assert expr_page.get_active_chips_count() == 1
    chip_text = (
        expr_page.page.locator(".expr-active-chips .filter-chip")
        .first.inner_text()
        .strip()
    )
    assert chip_text == "Mature: hsa-let-7a-5p"

    expr_page.select_expression_change("Upregulated")
    assert expr_page.get_active_indicator_text() == "2 Active: 1 Mature, Upregulated"
    assert expr_page.get_active_chips_count() == 2

    expr_page.reset_expression_filters()
    assert expr_page.get_filtered_total() == 524
    assert expr_page.get_active_indicator_text() == "No Filters Active"
    assert expr_page.get_active_chips_count() == 0


def test_expression_card_categorical_and_combined_filters(
    app_page: Page, base_url: str
):
    """Verify Expression categorical selects and combined multi-filter AND logic."""
    expr_page = ExpressionPage(app_page, base_url)
    expr_page.navigate_to_expression()

    expr_page.select_expression_change("Upregulated")
    assert expr_page.get_filtered_total() == 276
    expr_page.reset_expression_filters()

    expr_page.select_overall_evidence("Conflicting evidence")
    assert expr_page.get_filtered_total() == 194
    expr_page.reset_expression_filters()

    # Combined: mature ID + change + evidence
    expr_page.filter_mature("hsa-let-7a-5p")
    expr_page.select_expression_change("Upregulated")
    expr_page.select_overall_evidence("Conflicting evidence")
    assert expr_page.get_filtered_total() == 3
    assert expr_page.get_active_chips_count() == 3


def test_expression_card_other_evidence_filter(app_page: Page, base_url: str):
    """Verify Expression inline card 'Evidence from other studies' multi-select filter."""
    expr_page = ExpressionPage(app_page, base_url)
    expr_page.navigate_to_expression()

    # Total unfiltered
    assert expr_page.get_filtered_total() == 524

    # Select CNV
    expr_page.select_other_evidence("CNV")
    assert expr_page.get_filtered_total() == 33
    assert expr_page.get_active_chips_count() == 1
    assert "1 Other Ev." in expr_page.get_active_indicator_text()
    chip_text = expr_page.page.locator(".expr-active-chips .filter-chip").first.inner_text().strip()
    assert "CNV" in chip_text

    # Multi-select: also select Bioinformatics
    expr_page.select_other_evidence("Bioinformatics")
    assert expr_page.get_filtered_total() == 68
    assert expr_page.get_active_chips_count() == 2

    # Reset
    expr_page.reset_expression_filters()
    assert expr_page.get_filtered_total() == 524
    assert expr_page.get_active_chips_count() == 0

    # Select No other studies (None)
    expr_page.select_other_evidence("no")
    assert expr_page.get_filtered_total() == 451
    expr_page.reset_expression_filters()
    assert expr_page.get_filtered_total() == 524


def test_genetic_card_mirna_filter_and_reset(app_page: Page, base_url: str):
    """Verify the Genetic & Other Studies inline card miRNA filter and reset."""
    gen_page = GeneticPage(app_page, base_url)
    gen_page.navigate_to_genetic()

    assert gen_page.get_filtered_total() == 93

    gen_page.filter_mature("miR-106b-5p")
    assert gen_page.get_filtered_total() == 1
    assert gen_page.get_active_chips_count() == 1
    assert gen_page.get_active_indicator_text().startswith("1 Active")

    gen_page.click_reset_filters()
    assert gen_page.get_filtered_total() == 93
    assert gen_page.get_active_chips_count() == 0
    assert gen_page.get_active_indicator_text() == "No Filters Active"


def test_genetic_card_combined_alteration_and_hairpin(
    app_page: Page, base_url: str
):
    """Verify Genetic alteration select and combined alteration + hairpin AND logic."""
    gen_page = GeneticPage(app_page, base_url)
    gen_page.navigate_to_genetic()

    gen_page.select_genetic_alteration("CNV")
    assert gen_page.get_filtered_total() == 57
    gen_page.click_reset_filters()

    # Combined: CNV + miRNA hairpin narrows to a single study
    gen_page.select_genetic_alteration("CNV")
    gen_page.filter_hairpin("hsa-mir-107")
    assert gen_page.get_filtered_total() == 1
    assert gen_page.get_active_chips_count() == 2
    assert gen_page.get_active_indicator_text() == "2 Active: 1 Hairpins, CNV"


def test_targets_card_gene_filter_and_reset(app_page: Page, base_url: str):
    """Verify the Target Genes inline card gene filter and clear-all reset."""
    targets_page = TargetsPage(app_page, base_url)
    targets_page.navigate_to_targets()

    assert targets_page.get_filtered_total() == 17150
    assert targets_page.get_active_genes_count_text() == "2,995"

    targets_page.search("PTEN")
    assert targets_page.get_filtered_total() == 82
    assert targets_page.get_active_genes_count_text() == "1"

    targets_page.reset_target_filters()
    assert targets_page.get_filtered_total() == 17150
    assert targets_page.get_active_genes_count_text() == "2,995"


def test_targets_view_mode_round_trip(app_page: Page, base_url: str):
    """Selecting a miRNA auto-scopes targets; view modes round-trip correctly."""
    expr_page = ExpressionPage(app_page, base_url)
    targets_page = TargetsPage(app_page, base_url)

    expr_page.navigate_to_expression()
    expr_page.select_row_by_index(0)

    # Selecting a miRNA auto-scopes the targets table (selected-miRNA view).
    targets_page.navigate_to_targets()
    assert targets_page.get_active_view_mode() == "selected-mirna"
    scoped = targets_page.get_filtered_total()
    assert 0 < scoped < 17150

    # Switching to "All" reveals the full catalog.
    targets_page.set_view_mode("all")
    assert targets_page.get_active_view_mode() == "all"
    assert targets_page.get_filtered_total() == 17150

    # Switching back to "Selected miRNAs" restores the scoped subset.
    targets_page.set_view_mode("selected-mirna")
    assert targets_page.get_active_view_mode() == "selected-mirna"
    assert targets_page.get_filtered_total() == scoped


def test_expression_card_methodology_and_diagnostic_filters(
    app_page: Page, base_url: str
):
    """Verify methodology and diagnostic tool multi-select filters on Expression Studies."""
    expr_page = ExpressionPage(app_page, base_url)
    expr_page.navigate_to_expression()

    assert expr_page.get_filtered_total() == 524

    # Select methodology RT-qPCR
    expr_page.select_methodology("RT-qPCR")
    assert expr_page.get_filtered_total() == 318
    assert expr_page.get_active_chips_count() == 1
    assert "1 Methods" in expr_page.get_active_indicator_text()
    chip_text = expr_page.page.locator(".expr-active-chips .filter-chip").first.inner_text().strip()
    assert "RT-qPCR" in chip_text

    # Multi-select methodology: also select Small RNA-seq (OR logic: 496)
    expr_page.select_methodology("Small RNA-seq")
    assert expr_page.get_filtered_total() == 496
    assert expr_page.get_active_chips_count() == 2

    # Uncheck Small RNA-seq
    expr_page.page.locator('#expr-methodology-checkboxes input[value="Small RNA-seq"]').uncheck()
    expr_page.page.wait_for_timeout(400)
    assert expr_page.get_filtered_total() == 318

    # Select diagnostic tool DSM-5 (AND logic: RT-qPCR + DSM-5 -> 142)
    expr_page.select_diagnostic_tool("DSM-5")
    assert expr_page.get_filtered_total() == 142
    assert expr_page.get_active_chips_count() == 2
    indicator = expr_page.get_active_indicator_text()
    assert "2 Active" in indicator

    # Reset expression filters
    expr_page.reset_expression_filters()
    assert expr_page.get_filtered_total() == 524
    assert expr_page.get_active_chips_count() == 0
    assert expr_page.get_active_indicator_text() == "No Filters Active"


def test_genetic_card_methodology_and_diagnostic_filters(
    app_page: Page, base_url: str
):
    """Verify methodology and diagnostic tool multi-select filters on Genetic Studies."""
    gen_page = GeneticPage(app_page, base_url)
    gen_page.navigate_to_genetic()

    assert gen_page.get_filtered_total() == 93

    # Select methodology WGS
    gen_page.select_methodology("WGS")
    assert gen_page.get_filtered_total() == 5
    assert gen_page.get_active_chips_count() == 1
    assert "1 Methods" in gen_page.get_active_indicator_text()

    # Select diagnostic tool DSM-5 (WGS + DSM-5 -> 5)
    gen_page.select_diagnostic_tool("DSM-5")
    assert gen_page.get_filtered_total() == 5
    assert gen_page.get_active_chips_count() == 2

    # Reset genetic filters
    gen_page.click_reset_filters()
    assert gen_page.get_filtered_total() == 93
    assert gen_page.get_active_chips_count() == 0
    assert gen_page.get_active_indicator_text() == "No Filters Active"

