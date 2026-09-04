"""End-to-end tests for Target Interaction Database Switcher & Table Filters."""

from playwright.sync_api import Page

from tests.e2e.pages.enrichment_page import EnrichmentPage
from tests.e2e.pages.targets_page import TargetsPage


def test_default_database_is_mirtarbase(app_page: Page, base_url: str):
    """Verify that Target Genes table initializes with miRTarBase 10.0 active."""
    targets_page = TargetsPage(app_page, base_url)
    targets_page.navigate_to_targets()

    # Active button should be miRTarBase
    assert targets_page.is_database_selected("mirtarbase"), (
        "Default selected database is not miRTarBase"
    )

    # Count badges should indicate 17,150 target interactions and 2,995 target genes
    count_text = targets_page.get_active_count_text()
    genes_count_text = targets_page.get_active_genes_count_text()
    assert "17,150" in count_text, f"Unexpected default interaction count: {count_text}"
    assert "2,995" in genes_count_text, (
        f"Unexpected default gene count: {genes_count_text}"
    )


def test_database_switcher_counts_and_isolation(app_page: Page, base_url: str):
    """Verify switching database updates interaction and gene counts dynamically."""
    targets_page = TargetsPage(app_page, base_url)
    targets_page.navigate_to_targets()

    # 1. Consensus mode (7,492 interactions, 2,130 unique genes)
    targets_page.select_database("consensus")
    assert "7,492" in targets_page.get_active_count_text()
    assert "2,130" in targets_page.get_active_genes_count_text()
    assert "Consensus" in targets_page.get_table_body_text()

    # 2. DIANA-TarBase v9.0 mode (68,495 interactions, 2,577 unique genes)
    targets_page.select_database("tarbase")
    assert "68,495" in targets_page.get_active_count_text()
    assert "2,577" in targets_page.get_active_genes_count_text()

    # 3. All Sources mode (78,153 interactions, 3,281 unique genes)
    targets_page.select_database("all")
    assert "78,153" in targets_page.get_active_count_text()
    assert "3,281" in targets_page.get_active_genes_count_text()

    # 4. Return to miRTarBase 10.0 mode (17,150 interactions, 2,995 unique genes)
    targets_page.select_database("mirtarbase")
    assert "17,150" in targets_page.get_active_count_text()
    assert "2,995" in targets_page.get_active_genes_count_text()


def test_cross_tab_database_synchronization(app_page: Page, base_url: str):
    """Verify database selection remains synchronized across all views."""
    targets_page = TargetsPage(app_page, base_url)
    enrichment_page = EnrichmentPage(app_page, base_url)

    targets_page.navigate_to_targets()

    # Switch to Consensus from the Enrichment tab
    enrichment_page.navigate_to_enrichment()
    enrichment_page.select_database("consensus")
    assert enrichment_page.is_database_selected("consensus")

    # Switch back to Target Genes tab and assert Consensus is selected and count updated
    targets_page.navigate_to_targets()
    assert targets_page.is_database_selected("consensus"), (
        "Target Genes tab radio failed to synchronize from Enrichment tab"
    )
    assert "7,492" in targets_page.get_active_count_text()

    # Open slide-over drawer and verify select element also matches
    targets_page.open_filter_drawer()
    drawer_db_val = app_page.locator("#filter-target-db").input_value()
    assert drawer_db_val == "consensus", (
        f"Filter drawer DB dropdown mismatch: {drawer_db_val}"
    )
    targets_page.close_filter_drawer()
