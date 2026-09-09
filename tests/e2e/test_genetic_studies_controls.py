"""End-to-end tests for Genetic & Other Studies toolbar buttons and table."""

from playwright.sync_api import Page

from tests.e2e.pages.genetic_page import GeneticPage


def test_genetic_select_visible_and_clear(app_page: Page, base_url: str):
    """Verify header select-all and global selection clearing on Genetic tab."""
    gen_page = GeneticPage(app_page, base_url)
    gen_page.navigate_to_genetic()

    # Initial state
    assert gen_page.get_selected_count() == "0"
    assert not gen_page.is_run_enrichment_button_enabled()

    # Check the header select-all checkbox to select all visible rows
    gen_page.click_header_select_all()
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
    """Verify alteration filter and expandable child row on Genetic Studies tab."""
    gen_page = GeneticPage(app_page, base_url)
    gen_page.navigate_to_genetic()

    # Filter by CNV alterations
    gen_page.select_genetic_alteration("CNV")
    assert gen_page.get_filtered_total() == 57

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

    assert gen_page.get_filtered_total() == 93

    # Apply a study description keyword filter
    gen_page.filter_study_desc("sequencing")
    assert gen_page.get_filtered_total() == 5

    gen_page.click_reset_filters()
    assert gen_page.get_filtered_total() == 93


def test_genetic_targets_count_updates_on_selection(app_page: Page, base_url: str):
    """Verify target genes count displays alongside miRNA counter and in CTA."""
    gen_page = GeneticPage(app_page, base_url)
    gen_page.navigate_to_genetic()

    # Initial state: 0 selected, 0 targets
    assert gen_page.get_selected_count() == "0"
    assert gen_page.get_targets_count() == "0"

    # Select miRNA row with known validated targets (e.g. miR-106b-5p at index 2)
    gen_page.select_row_by_index(2)
    assert gen_page.get_selected_count() == "1"

    targets_count = gen_page.get_targets_count()
    assert int(targets_count) > 0, f"Expected >0 targets, got {targets_count}"

    # The Target Genes CTA text should contain both miRNAs and Targets
    cta_text = gen_page.get_run_enrichment_button_text()
    assert "1 Selected miRNAs" in cta_text
    assert f"{targets_count} Targets" in cta_text

    # Clear selection returns counts to 0
    gen_page.click_clear_selection()
    assert gen_page.get_selected_count() == "0"
    assert gen_page.get_targets_count() == "0"
