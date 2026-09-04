"""End-to-end tests for Expression Studies toolbar buttons, table, and selection."""

from playwright.sync_api import Page

from tests.e2e.pages.expression_page import ExpressionPage


def test_expression_select_visible_and_clear_selection(app_page: Page, base_url: str):
    """Verify 'Select Visible' and 'Clear Selection' buttons update state."""
    expr_page = ExpressionPage(app_page, base_url)
    expr_page.navigate_to_expression()

    # Initial state: 0 selected and analyze CTA disabled
    assert expr_page.get_selected_count() == "0"
    assert not expr_page.is_run_enrichment_button_enabled()

    # Click 'Select Visible'
    expr_page.click_select_visible()
    selected_count = expr_page.get_selected_count()
    assert int(selected_count) > 0, (
        f"Expected positive selected count, got {selected_count}"
    )
    assert expr_page.is_run_enrichment_button_enabled(), (
        "Analyze CTA should be enabled when miRNAs are selected"
    )

    # Click 'Clear Selection'
    expr_page.click_clear_selection()
    assert expr_page.get_selected_count() == "0"
    assert not expr_page.is_run_enrichment_button_enabled(), (
        "Analyze CTA should be disabled after clearing selection"
    )


def test_expression_header_select_all_toggle(app_page: Page, base_url: str):
    """Verify table header master checkbox toggles all visible row checkboxes."""
    expr_page = ExpressionPage(app_page, base_url)
    expr_page.navigate_to_expression()

    # Toggle header checkbox to check all
    expr_page.click_header_select_all()
    assert expr_page.is_header_select_all_checked()
    assert int(expr_page.get_selected_count()) > 0

    # Toggle header checkbox again to uncheck all
    expr_page.click_header_select_all()
    assert not expr_page.is_header_select_all_checked()
    assert expr_page.get_selected_count() == "0"


def test_expression_table_search_and_pagination(app_page: Page, base_url: str):
    """Verify search input filters rows and pagination controls navigate."""
    expr_page = ExpressionPage(app_page, base_url)
    expr_page.navigate_to_expression()

    initial_count = expr_page.get_row_count()
    assert initial_count > 0

    # Filter with specific miRNA symbol
    expr_page.search("miR-132")
    filtered_count = expr_page.get_row_count()
    assert 0 < filtered_count <= initial_count

    # Clear search
    expr_page.search("")
    assert expr_page.get_row_count() == initial_count

    # Pagination navigation to page 2
    expr_page.click_page(2)
    assert expr_page.get_row_count() > 0


def test_expression_child_row_details_expand(app_page: Page, base_url: str):
    """Verify row details control toggles expandable child row with metadata."""
    expr_page = ExpressionPage(app_page, base_url)
    expr_page.navigate_to_expression()

    # Expand details
    expr_page.expand_row_details(0)
    assert expr_page.is_child_row_visible()

    # Collapse details
    expr_page.expand_row_details(0)
    assert not expr_page.is_child_row_visible()


def test_expression_reset_filters_button(app_page: Page, base_url: str):
    """Verify 'Reset Filters' toolbar button clears search and active state."""
    expr_page = ExpressionPage(app_page, base_url)
    expr_page.navigate_to_expression()

    initial_rows = expr_page.get_row_count()

    # Apply search filter
    expr_page.search("hsa-let-7a-5p")
    assert expr_page.get_row_count() < initial_rows

    # Click Reset Filters
    expr_page.click_reset_filters()
    assert expr_page.get_row_count() == initial_rows
