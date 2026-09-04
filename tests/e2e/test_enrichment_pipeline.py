"""End-to-end tests for Functional Enrichment (g:Profiler) workflow."""

from playwright.sync_api import Page

from tests.e2e.pages.enrichment_page import EnrichmentPage
from tests.e2e.pages.expression_page import ExpressionPage


def test_enrichment_awaiting_mirna_selection_state(app_page: Page, base_url: str):
    """Verify Functional Enrichment starts in awaiting state with disabled button."""
    enrichment_page = EnrichmentPage(app_page, base_url)
    enrichment_page.navigate_to_enrichment()

    # Step 1 guidance prompt should be visible
    assert enrichment_page.is_awaiting_selection_prompt_visible(), (
        "Expected 'Step 1: Select miRNAs to Analyze' prompt on unselected state"
    )

    # CTA button should be disabled
    assert not enrichment_page.is_run_button_enabled(), (
        "Run Enrichment CTA button should be disabled before selecting miRNAs"
    )


def test_enrichment_db_buttons_interactive_before_selection(
    app_page: Page, base_url: str
):
    """Verify database buttons on enrichment tab are clickable with 0 miRNAs."""
    enrichment_page = EnrichmentPage(app_page, base_url)
    enrichment_page.navigate_to_enrichment()

    for db_name in ["mirtarbase", "consensus", "tarbase", "all"]:
        assert not enrichment_page.is_database_button_disabled(db_name), (
            f"Database '{db_name}' should NOT be disabled when 0 miRNAs selected"
        )


def test_mirna_selection_to_enrichment_flow(app_page: Page, base_url: str):
    """Verify selecting distinct miRNAs resolves targets and enables enrichment."""
    expr_page = ExpressionPage(app_page, base_url)
    enrichment_page = EnrichmentPage(app_page, base_url)

    expr_page.navigate_to_expression()

    # Select two distinct microRNAs (row 0: hsa-let-7a-5p, row 6: hsa-let-7b-5p)
    expr_page.select_row_by_index(0)
    expr_page.select_row_by_index(6)

    # Selection counter should indicate 2
    assert expr_page.get_selected_count() == "2", (
        "Expected 2 selected miRNAs in counter"
    )

    # Click the contextual Run Enrichment CTA button to switch to enrichment tab
    expr_page.click_run_target_enrichment_button()

    # Awaiting prompt should now be replaced with target gene chips
    assert not enrichment_page.is_awaiting_selection_prompt_visible(), (
        "Awaiting selection prompt should be cleared once miRNAs are selected"
    )
    chips_text = enrichment_page.get_chips_content()
    assert len(chips_text) > 0, "No target gene chips populated for selected miRNAs"

    # CTA button should now be enabled and report gene count
    assert enrichment_page.is_run_button_enabled(), (
        "Run Enrichment CTA should be enabled"
    )
    btn_text = enrichment_page.get_run_button_text()
    assert "Run g:Profiler Functional Enrichment" in btn_text
    assert "Target Genes" in btn_text
