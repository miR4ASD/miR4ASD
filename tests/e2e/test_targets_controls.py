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


def test_targets_sfari_symbol_badges(app_page: Page, base_url: str):
    """Verify SFARI category and syndromic symbol tokens render without star icons."""
    targets_page = TargetsPage(app_page, base_url)
    targets_page.navigate_to_targets()

    # 1. Legend should feature SFARI token badges: 1, 2, 3, S, and 2S
    assert app_page.locator("#targets .sfari-tag-cat1").first.is_visible()
    assert app_page.locator("#targets .sfari-tag-cat2").first.is_visible()
    assert app_page.locator("#targets .sfari-tag-cat3").first.is_visible()
    assert app_page.locator("#targets .sfari-tag-syn").first.is_visible()

    # 2. Verify star icons are eliminated across targets table and controls
    assert app_page.locator("#targets .fa-star").count() == 0
    assert app_page.locator("#targets .fa-star-half-stroke").count() == 0

    # 3. Search for CNTNAP2 (Category 2, Syndromic) in targets table
    targets_page.search("CNTNAP2")
    composite_cell = app_page.locator("#targets-table tbody tr .sfari-tag-group").first
    assert composite_cell.is_visible()
    assert composite_cell.locator(".sfari-tag-cat2").inner_text() == "2"
    assert composite_cell.locator(".sfari-tag-syn").inner_text() == "S"

    # 4. Search for ANK2 (Category 1) in targets table
    targets_page.search("ANK2")
    cat1_cell = app_page.locator("#targets-table tbody tr .sfari-tag-cat1").first
    assert cat1_cell.is_visible()
    assert cat1_cell.inner_text() == "1"


def test_targets_filter_non_sfari_checkbox(app_page: Page, base_url: str):
    """Verify selecting 'None (Non-SFARI)' checkbox filters to Non-SFARI genes with None badge."""
    targets_page = TargetsPage(app_page, base_url)
    targets_page.navigate_to_targets()

    # Filter by Non-SFARI checkbox
    targets_page.select_sfari_category("Non-SFARI")
    rows = targets_page.get_row_count()
    assert rows > 0

    # Every visible row in SFARI column should display 'None'
    badges = app_page.locator("#targets-table tbody tr td:nth-child(6) .badge").all_inner_texts()
    assert len(badges) > 0
    assert all(b.strip() == "None" for b in badges)

    # Verify DataTables search input has the enhanced placeholder
    search_input = app_page.locator("#targets-table_wrapper .dt-search input, #targets-table_wrapper input[type='search']")
    placeholder = search_input.get_attribute("placeholder") or ""
    assert "Search" in placeholder

