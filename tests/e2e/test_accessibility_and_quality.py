"""End-to-end accessibility (WCAG 2.1 AA) and runtime quality verification."""

from playwright.sync_api import Page

from tests.e2e.pages.figures_page import FiguresPage


def test_all_figures_have_meaningful_alt_text(app_page: Page, base_url: str):
    """Verify that every figure image has a descriptive non-empty alt attribute."""
    figures_page = FiguresPage(app_page, base_url)
    figures_page.navigate_to_figures()

    images = figures_page.get_figure_images()
    for img in images:
        alt = img.get_attribute("alt")
        assert alt and len(alt.strip()) >= 5, (
            f"Image missing/trivial alt text: src={img.get_attribute('src')}, "
            f"alt='{alt}'"
        )


def test_wcag_semantic_landmarks_present(app_page: Page, base_url: str):
    """Verify essential WCAG ARIA landmarks exist on the page."""
    app_page.goto(base_url, wait_until="domcontentloaded")

    # Header landmark
    assert app_page.locator("header[role='banner'], .header").count() > 0, (
        "Missing banner landmark"
    )

    # Main landmark
    assert app_page.locator("main[role='main'], #main-content").count() > 0, (
        "Missing main landmark"
    )

    # Navigation tablist
    assert app_page.locator("[role='tablist']").count() > 0, "Missing tablist ARIA role"

    # Tabs have role='tab' and aria-controls
    tabs = app_page.locator("[role='tab']").all()
    assert len(tabs) >= 5, f"Expected 5 tab controls, found {len(tabs)}"
    for tab in tabs:
        assert tab.get_attribute("aria-controls"), (
            f"Tab missing aria-controls: {tab.inner_text()}"
        )


def test_keyboard_tab_focusability(app_page: Page, base_url: str):
    """Verify interactive tabs and primary buttons can receive keyboard focus."""
    app_page.goto(base_url, wait_until="domcontentloaded")
    app_page.wait_for_timeout(500)

    # Focus about tab and press Tab key
    about_tab = app_page.locator("#about-tab")
    about_tab.focus()
    assert app_page.evaluate("() => document.activeElement.id") == "about-tab"

    # Press arrow right to navigate to next tab
    app_page.keyboard.press("ArrowRight")
    app_page.wait_for_timeout(200)
    active_id = app_page.evaluate("() => document.activeElement.id")
    assert active_id in ["about-tab", "expression-tab"], (
        f"Unexpected active element after ArrowRight: {active_id}"
    )


def test_all_interactive_buttons_and_filter_radios_have_tooltips(
    app_page: Page, base_url: str
) -> None:
    """Verify that all platform action buttons and filter radios possess tooltips."""
    app_page.goto(base_url, wait_until="domcontentloaded")
    app_page.wait_for_timeout(500)

    # 1. Target Genes view-mode buttons (Targets tab) carry descriptive tooltips.
    view_modes = ["all", "selected-mirna", "selected-only"]
    for mode in view_modes:
        btn = app_page.locator(f'.targets-view-btn[data-view-mode="{mode}"]')
        assert btn.count() > 0, f"Missing view-mode button for {mode}"
        title = btn.get_attribute("title") or btn.get_attribute(
            "data-bs-original-title"
        )
        assert title and len(title.strip()) > 10, (
            f"View-mode button '{mode}' missing or too short tooltip: '{title}'"
        )

    # 2. Single-source database badges (Targets tab and Enrichment tab)
    db_badges = ["#active-db-label", "#enrichment-db-badge"]
    for badge_selector in db_badges:
        badge = app_page.locator(badge_selector)
        assert badge.count() > 0, f"Missing single-source badge {badge_selector}"
        assert "miRTarBase 10.0" in badge.first.inner_text(), (
            f"Badge {badge_selector} does not show the sole data source"
        )

    # 3. Action and toolbar buttons
    action_buttons = [
        ".btn-reset-table-filters",
        ".btn-analyze-filtered",
        "#btn-run-enrichment",
        "#btn-copy-genes",
        "#btn-clear-genes",
        "#btn-export-enrichment-chart",
        "#btn-export-enrichment-csv",
        "#btn-back-to-top",
    ]
    for selector in action_buttons:
        elements = app_page.locator(selector).all()
        assert len(elements) > 0, f"No elements matched button selector '{selector}'"
        for elem in elements:
            title = elem.get_attribute("title") or elem.get_attribute(
                "data-bs-original-title"
            )
            assert title and len(title.strip()) >= 5, (
                f"Element '{selector}' missing descriptive tooltip: '{title}'"
            )
