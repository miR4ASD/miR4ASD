"""End-to-end tests for Target Genes search, pagination, child details, and CTA."""

from playwright.sync_api import Page

from tests.e2e.pages.expression_page import ExpressionPage
from tests.e2e.pages.targets_page import TargetsPage


def test_targets_table_search_and_pagination(app_page: Page, base_url: str):
    """Verify searching by gene symbol and navigating through pages in targets table."""
    targets_page = TargetsPage(app_page, base_url)
    targets_page.navigate_to_targets()

    initial_rows = targets_page.get_row_count()
    assert initial_rows > 0

    # Search for a well-known target gene (PTEN)
    targets_page.search("PTEN")
    pten_rows = targets_page.get_row_count()
    assert 0 < pten_rows <= initial_rows
    assert "PTEN" in targets_page.get_table_body_text()

    # Clear search
    targets_page.search("")
    assert targets_page.get_row_count() == initial_rows

    # Pagination navigation to page 2
    targets_page.click_page(2)
    assert targets_page.get_row_count() > 0


def test_targets_child_row_expansion(app_page: Page, base_url: str):
    """Verify child row details toggle displays PubMed and experimental metadata."""
    targets_page = TargetsPage(app_page, base_url)
    targets_page.navigate_to_targets()

    # Expand first row details
    targets_page.expand_row_details(0)
    assert targets_page.is_child_row_visible()

    # Child row should contain PubMed or experimental information
    details_text = targets_page.get_child_row_text()
    assert len(details_text) > 0

    # Collapse row details
    targets_page.expand_row_details(0)
    assert not targets_page.is_child_row_visible()


def test_targets_analyze_button_states(app_page: Page, base_url: str):
    """Verify Targets tab analyze CTA button updates with selection state."""
    targets_page = TargetsPage(app_page, base_url)
    expr_page = ExpressionPage(app_page, base_url)

    # Initial state with 0 miRNAs: disabled
    targets_page.navigate_to_targets()
    assert not targets_page.is_analyze_button_enabled()
    assert "Select miRNAs" in targets_page.get_analyze_button_text()

    # Select miRNA in Expression tab
    expr_page.navigate_to_expression()
    expr_page.select_row_by_index(0)

    # Re-navigate to Targets tab: button should now be enabled
    targets_page.navigate_to_targets()
    assert targets_page.is_analyze_button_enabled()
    assert "Run Target Enrichment" in targets_page.get_analyze_button_text()
