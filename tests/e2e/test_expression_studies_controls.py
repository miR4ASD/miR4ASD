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


def test_expression_evidence_multiselect_or_and_chips(app_page: Page, base_url: str):
    """Verify Overall Evidence multi-select OR semantics and chip dismissal."""
    expr_page = ExpressionPage(app_page, base_url)
    expr_page.navigate_to_expression()

    assert expr_page.get_filtered_total() == 524

    # First value only: Consistent upregulation -> 42 rows
    expr_page.select_overall_evidence("Consistent upregulation")
    assert expr_page.get_filtered_total() == 42
    assert expr_page.get_active_chips_count() == 1

    # Second value accumulates (multi-select) OR semantics: 42 + 19 = 61
    expr_page.select_overall_evidence("Consistent downregulation")
    assert expr_page.get_filtered_total() == 61
    assert expr_page.get_active_chips_count() == 2

    # Dismissing the downregulation chip clears only that value, leaving
    # Consistent upregulation active (42 rows, 1 chip)
    down_chip_text = "Evidence: Consistent downregulation"
    chip = app_page.locator(
        ".expr-active-chips .filter-chip", has_text=down_chip_text
    ).first
    chip.locator("i.chip-remove").click()
    app_page.wait_for_timeout(400)
    assert expr_page.get_filtered_total() == 42
    assert expr_page.get_active_chips_count() == 1

    # Per-tab reset returns to the full set
    expr_page.reset_expression_filters()
    assert expr_page.get_filtered_total() == 524
    assert expr_page.get_active_chips_count() == 0


def test_expression_numeric_min_study_filters(app_page: Page, base_url: str):
    """Verify Min # up / Min # down / Min total numeric filters AND-combine."""
    expr_page = ExpressionPage(app_page, base_url)
    expr_page.navigate_to_expression()

    assert expr_page.get_filtered_total() == 524

    # Min # up >= 3 -> 52 rows (1 chip)
    expr_page.set_min_upregulation_studies("3")
    assert expr_page.get_filtered_total() == 52
    assert expr_page.get_active_chips_count() == 1

    # Min # down >= 3 on top -> AND: 12 rows (2 chips)
    expr_page.set_min_downregulation_studies("3")
    assert expr_page.get_filtered_total() == 12
    assert expr_page.get_active_chips_count() == 2

    # Min total >= 5 on top -> AND: 12 rows (3 chips)
    expr_page.set_min_total_studies("5")
    assert expr_page.get_filtered_total() == 12
    assert expr_page.get_active_chips_count() == 3

    # Clearing one numeric input relaxes its criterion (back to 12, 2 chips)
    expr_page.set_min_total_studies("")
    assert expr_page.get_filtered_total() == 12
    assert expr_page.get_active_chips_count() == 2

    expr_page.reset_expression_filters()
    assert expr_page.get_filtered_total() == 524
    assert expr_page.get_active_chips_count() == 0


def test_expression_evidence_and_numeric_min_combine(app_page: Page, base_url: str):
    """Verify the evidence checklist and a numeric min filter AND-combine."""
    expr_page = ExpressionPage(app_page, base_url)
    expr_page.navigate_to_expression()

    assert expr_page.get_filtered_total() == 524

    # Evidence: Consistent upregulation -> 42 rows
    expr_page.select_overall_evidence("Consistent upregulation")
    assert expr_page.get_filtered_total() == 42

    # + Min total >= 3 -> 12 rows (2 chips: 1 evidence + 1 numeric)
    expr_page.set_min_total_studies("3")
    assert expr_page.get_filtered_total() == 12
    assert expr_page.get_active_chips_count() == 2

    expr_page.reset_expression_filters()
    assert expr_page.get_filtered_total() == 524


def test_expression_headers_renamed_up_down(app_page: Page, base_url: str):
    """Verify the expression table headers show the short # up / # down labels."""
    expr_page = ExpressionPage(app_page, base_url)
    expr_page.navigate_to_expression()

    th_selector = "#expression-table thead th"
    js = "Array.from(document.querySelectorAll('" + th_selector + "'))"
    js += ".map(th => th.textContent.trim())"
    header_texts = app_page.evaluate(js)
    assert "# up" in header_texts
    assert "# down" in header_texts
    # The verbose legacy labels are no longer used as headers
    assert not any("number of studies" in h.lower() for h in header_texts)


def test_expression_subtable_sample_badges_and_headers(app_page: Page, base_url: str):
    """Verify subtable headers show Sample Type/Subtype and multi-cohort samples render as distinct badges."""
    expr_page = ExpressionPage(app_page, base_url)
    expr_page.navigate_to_expression()

    # Expand details for first row (contains Huang 2015 with multi-cohort sample counts)
    expr_page.expand_row_details(0)
    assert expr_page.is_child_row_visible()

    child = app_page.locator(
        "#expression-table tbody tr.child, #expression-table tbody tr.details + tr"
    ).first
    child_text = child.inner_text().lower()
    assert "sample type" in child_text
    assert "sample subtype" in child_text

    # Verify separate pill badges are rendered for semicolon-separated sample counts
    sample_badges = child.locator("td span.badge.rounded-pill")
    badge_texts = sample_badges.all_inner_texts()
    assert any("Microarray ASD N = 5" in b for b in badge_texts)
    assert any("RT-qPCR ASD N = 15" in b for b in badge_texts)
    assert any("Microarray control N = 5" in b for b in badge_texts)
    assert any("RT-qPCR control N = 15" in b for b in badge_texts)
