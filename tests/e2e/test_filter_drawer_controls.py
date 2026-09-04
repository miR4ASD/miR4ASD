"""End-to-end tests for Slide-over Advanced Filter Drawer controls and workflows."""

from playwright.sync_api import Page

from tests.e2e.pages.drawer_page import DrawerPage
from tests.e2e.pages.expression_page import ExpressionPage


def test_drawer_open_and_close_methods(app_page: Page, base_url: str):
    """Verify drawer opens and closes via close icon, apply button, and backdrop."""
    drawer_page = DrawerPage(app_page, base_url)
    drawer_page.navigate()

    # 1. Close via 'X' icon
    drawer_page.open_drawer()
    assert drawer_page.is_drawer_open()
    drawer_page.close_drawer_via_icon()
    assert not drawer_page.is_drawer_open()

    # 2. Close via 'Apply & Close' footer button
    drawer_page.open_drawer()
    assert drawer_page.is_drawer_open()
    drawer_page.close_drawer_via_apply_button()
    assert not drawer_page.is_drawer_open()

    # 3. Close via backdrop click
    drawer_page.open_drawer()
    assert drawer_page.is_drawer_open()
    drawer_page.close_drawer_via_backdrop()
    assert not drawer_page.is_drawer_open()


def test_drawer_search_mode_switcher_tabs(app_page: Page, base_url: str):
    """Verify switching between Mature, Precursor, and Target Gene search modes."""
    drawer_page = DrawerPage(app_page, base_url)
    drawer_page.navigate()
    drawer_page.open_drawer()

    # Switch to Precursor mode
    drawer_page.set_search_mode("hairpin")
    assert app_page.locator("#pane-hairpin").is_visible()
    assert not app_page.locator("#pane-mature").is_visible()

    # Switch to Target Gene mode
    drawer_page.set_search_mode("gene")
    assert app_page.locator("#pane-gene").is_visible()
    assert not app_page.locator("#pane-hairpin").is_visible()

    # Switch back to Mature mode
    drawer_page.set_search_mode("mature")
    assert app_page.locator("#pane-mature").is_visible()
    assert not app_page.locator("#pane-gene").is_visible()


def test_drawer_filters_and_count_badge(app_page: Page, base_url: str):
    """Verify setting filter options updates active filter count and reset cleans it."""
    drawer_page = DrawerPage(app_page, base_url)
    drawer_page.navigate()
    drawer_page.open_drawer()

    # Initial state: 0 Active
    assert "0" in drawer_page.get_filter_count_badge_text()

    # Select SFARI Category 1
    drawer_page.select_sfari_category("Category 1")
    assert "1" in drawer_page.get_filter_count_badge_text()

    # Select Strong Evidence
    drawer_page.select_evidence_level("Strong Evidence")
    assert "2" in drawer_page.get_filter_count_badge_text()

    # Click Reset link in header
    drawer_page.click_reset_filters_header()
    assert "0" in drawer_page.get_filter_count_badge_text()


def test_drawer_deselect_button(app_page: Page, base_url: str):
    """Verify 'Deselect' button in drawer header clears table selection."""
    expr_page = ExpressionPage(app_page, base_url)
    drawer_page = DrawerPage(app_page, base_url)

    expr_page.navigate_to_expression()
    expr_page.select_row_by_index(0)

    # Open drawer and verify selection badge
    drawer_page.open_drawer()
    assert "1" in drawer_page.get_selection_badge_text()

    # Click Deselect
    drawer_page.click_deselect_header()
    assert "0" in drawer_page.get_selection_badge_text()


def test_drawer_enrich_action_button(app_page: Page, base_url: str):
    """Verify clicking quick enrichment button in drawer navigates to Enrichment tab."""
    expr_page = ExpressionPage(app_page, base_url)
    drawer_page = DrawerPage(app_page, base_url)

    expr_page.navigate_to_expression()
    expr_page.select_row_by_index(0)

    # Open drawer and click enrich
    drawer_page.open_drawer()
    drawer_page.click_drawer_enrich_button()

    # Should navigate to Functional Enrichment tab
    assert app_page.locator("#enrichment.tab-pane.active").is_visible()
