"""End-to-end tests for Genetic & Other Studies toolbar buttons and table."""

from playwright.sync_api import Page

from tests.e2e.pages.genetic_page import GeneticPage


def test_genetic_select_visible_and_clear(app_page: Page, base_url: str):
    """Verify 'Select Visible' and 'Clear Selection' on Genetic Studies tab."""
    gen_page = GeneticPage(app_page, base_url)
    gen_page.navigate_to_genetic()

    # Initial state
    assert gen_page.get_selected_count() == "0"
    assert not gen_page.is_run_enrichment_button_enabled()

    # Click Select Visible
    gen_page.click_select_visible()
    count = gen_page.get_selected_count()
    assert int(count) > 0
    assert gen_page.is_run_enrichment_button_enabled()

    # Click Clear Selection
    gen_page.click_clear_selection()
    assert gen_page.get_selected_count() == "0"
    assert not gen_page.is_run_enrichment_button_enabled()


def test_genetic_header_select_all(app_page: Page, base_url: str):
    """Verify master checkbox in Genetic table header toggles all rows."""
    gen_page = GeneticPage(app_page, base_url)
    gen_page.navigate_to_genetic()

    # Check all
    gen_page.click_header_select_all()
    assert gen_page.is_header_select_all_checked()
    assert int(gen_page.get_selected_count()) > 0

    # Uncheck all
    gen_page.click_header_select_all()
    assert not gen_page.is_header_select_all_checked()
    assert gen_page.get_selected_count() == "0"


def test_genetic_search_and_row_details(app_page: Page, base_url: str):
    """Verify search filter and expandable child row on Genetic Studies tab."""
    gen_page = GeneticPage(app_page, base_url)
    gen_page.navigate_to_genetic()

    initial_count = gen_page.get_row_count()

    # Search for CNV
    gen_page.search("CNV")
    filtered = gen_page.get_row_count()
    assert 0 < filtered <= initial_count

    # Expand row details
    gen_page.expand_row_details(0)
    assert gen_page.is_child_row_visible()

    # Collapse row details
    gen_page.expand_row_details(0)
    assert not gen_page.is_child_row_visible()


def test_genetic_reset_filters_button(app_page: Page, base_url: str):
    """Verify toolbar 'Reset Filters' clears search filter in Genetic tab."""
    gen_page = GeneticPage(app_page, base_url)
    gen_page.navigate_to_genetic()

    initial_count = gen_page.get_row_count()
    gen_page.search("sequencing")
    assert gen_page.get_row_count() < initial_count

    gen_page.click_reset_filters()
    assert gen_page.get_row_count() == initial_count
