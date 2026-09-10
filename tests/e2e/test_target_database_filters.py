"""End-to-end tests for the Target Genes single-source badge and inline filters."""

from playwright.sync_api import Page

from tests.e2e.pages.enrichment_page import EnrichmentPage
from tests.e2e.pages.targets_page import TargetsPage


def test_default_database_is_mirtarbase(app_page: Page, base_url: str):
    """Verify that Target Genes initializes with the single miRTarBase 10.0 source."""
    targets_page = TargetsPage(app_page, base_url)
    targets_page.navigate_to_targets()

    assert targets_page.is_single_source_mirtarbase()
    assert targets_page.get_database_badge_text() == "miRTarBase 10.0"

    # Count badges: 17,150 target interactions / 2,995 target genes
    assert targets_page.get_active_count_text() == "17,150"
    assert targets_page.get_active_genes_count_text() == "2,995"


def test_inline_filter_counts(app_page: Page, base_url: str):
    """Verify each inline Target Genes filter narrows interaction/gene counts."""
    targets_page = TargetsPage(app_page, base_url)
    targets_page.navigate_to_targets()

    cases = [
        (lambda: targets_page.search("PTEN"), "82", "1"),
        (lambda: targets_page.search("CNTNAP2"), "20", "1"),
        (lambda: targets_page.search("ANK2"), "27", "1"),
        (lambda: targets_page.select_sfari_category("Category 1"), "2,567", "143"),
        (
            lambda: targets_page.select_evidence_level("Strong Evidence"),
            "5,730",
            "2,372",
        ),
        (
            lambda: targets_page.select_method("Luciferase Reporter Assay"),
            "5,051",
            "2,204",
        ),
    ]
    for apply_filter, expected_interactions, expected_genes in cases:
        apply_filter()
        assert targets_page.get_active_count_text() == expected_interactions
        assert targets_page.get_active_genes_count_text() == expected_genes
        # 'Clear All' is only actionable while a filter chip is active
        targets_page.reset_target_filters()

    # Baseline restored after the final clear-all
    assert targets_page.get_active_count_text() == "17,150"
    assert targets_page.get_active_genes_count_text() == "2,995"


def test_cross_tab_single_source_synchronization(app_page: Page, base_url: str):
    """Verify the single-source badge is consistent across Targets and Enrichment."""
    targets_page = TargetsPage(app_page, base_url)
    enrichment_page = EnrichmentPage(app_page, base_url)

    targets_page.navigate_to_targets()
    assert targets_page.is_single_source_mirtarbase()
    assert targets_page.get_database_badge_text() == "miRTarBase 10.0"

    enrichment_page.navigate_to_enrichment()
    assert enrichment_page.is_single_source_mirtarbase()
    assert enrichment_page.get_database_badge_text() == "miRTarBase 10.0"


def test_sfari_susceptibility_multiselect_or_and_chips(app_page: Page, base_url: str):
    """Verify ASD Susceptibility is a multi-select with OR semantics and chips."""
    targets_page = TargetsPage(app_page, base_url)
    targets_page.navigate_to_targets()
    assert targets_page.get_filtered_total() == 17150

    # Single value: Category 1 -> 2,567 interactions
    targets_page.select_sfari_category("Category 1")
    assert targets_page.get_filtered_total() == 2567

    # Second value accumulates (multi-select) with OR semantics:
    # Category 1 (2,567) union Syndromic (1,800); no "Category 1, Syndromic"
    # score exists, so the sets are disjoint -> 4,367 interactions.
    targets_page.select_sfari_category("Syndromic")
    assert targets_page.get_filtered_total() == 4367
    # Dismissing the Category 1 chip leaves only Syndromic active (1,800)
    chip = app_page.locator(
        ".target-active-chips .filter-chip", has_text="SFARI: Category 1"
    ).first
    chip.locator("i.chip-remove").click()
    app_page.wait_for_timeout(400)
    assert targets_page.get_filtered_total() == 1800

    # Per-tab reset returns to the full set
    targets_page.reset_target_filters()
    assert targets_page.get_filtered_total() == 17150
