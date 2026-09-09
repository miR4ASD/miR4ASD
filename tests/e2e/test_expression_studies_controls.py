"""End-to-end tests for Expression Studies toolbar buttons, table, and selection."""

from playwright.sync_api import Page

from tests.e2e.pages.expression_page import ExpressionPage


def test_expression_select_visible_and_clear_selection(app_page: Page, base_url: str):
    """Verify header select-all and global selection clearing update state."""
    expr_page = ExpressionPage(app_page, base_url)
    expr_page.navigate_to_expression()

    # Initial state: 0 selected and enrichment CTA disabled
    assert expr_page.get_selected_count() == "0"
    assert not expr_page.is_run_enrichment_button_enabled()

    # Check the header select-all checkbox to select all visible rows
    expr_page.click_header_select_all()
    selected_count = expr_page.get_selected_count()
    assert int(selected_count) > 0, (
        f"Expected positive selected count, got {selected_count}"
    )
    assert expr_page.is_run_enrichment_button_enabled(), (
        "Enrichment CTA should be enabled when miRNAs are selected"
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
    """Verify inline miRNA filters rows and pagination controls navigate."""
    expr_page = ExpressionPage(app_page, base_url)
    expr_page.navigate_to_expression()

    assert expr_page.get_filtered_total() == 524

    # Filter with a specific miRNA hairpin ID
    expr_page.filter_hairpin("hsa-mir-132")
    assert expr_page.get_filtered_total() == 3

    # Clear the filter
    expr_page.filter_hairpin("")
    assert expr_page.get_filtered_total() == 524

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

    assert expr_page.get_filtered_total() == 524

    # Select first miRNA row
    expr_page.select_row_by_index(0)
    assert expr_page.get_selected_count() == "1"

    targets_count = expr_page.get_targets_count()
    assert int(targets_count) > 0, f"Expected >0 targets, got {targets_count}"

    # The Target Genes CTA text should contain both miRNAs and Targets
    cta_text = expr_page.get_run_enrichment_button_text()
    assert "1 Selected miRNAs" in cta_text
    assert f"{targets_count} Targets" in cta_text

    # Clear selection returns counts to 0
    expr_page.click_clear_selection()
    assert expr_page.get_selected_count() == "0"
    assert expr_page.get_targets_count() == "0"
