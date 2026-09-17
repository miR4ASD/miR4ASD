"""End-to-end tests for Database Statistics & Visualizations section."""

from playwright.sync_api import Page

from tests.e2e.pages.figures_page import FiguresPage


def test_all_figures_load_with_positive_dimensions(app_page: Page, base_url: str):
    """Verify all figures render successfully with positive natural dimensions."""
    figures_page = FiguresPage(app_page, base_url)
    figures_page.navigate_to_figures()

    images = figures_page.get_figure_images()
    assert len(images) >= 8, f"Expected at least 8 figure images, found {len(images)}"

    for idx, img in enumerate(images):
        src = img.get_attribute("src") or ""
        alt = img.get_attribute("alt") or f"Figure {idx + 1}"
        assert src, f"Image {alt} lacks src attribute"

        w, h = figures_page.get_image_natural_dimensions(img)
        assert w > 0, f"Figure '{alt}' ({src}) failed to load! (naturalWidth={w})"
        assert h > 0, f"Figure '{alt}' ({src}) failed to load! (naturalHeight={h})"
        assert img.is_visible(), f"Figure '{alt}' ({src}) is not visible on page!"


def test_figure_cards_do_not_open_modal_on_click(app_page: Page, base_url: str):
    """Verify clicking figure card displays it inline without opening a modal."""
    figures_page = FiguresPage(app_page, base_url)
    figures_page.navigate_to_figures()

    figures_page.click_figure_card(0)
    assert not figures_page.is_modal_present_or_visible(), (
        "Lightbox modal or backdrop appeared on figure click when it should be dropped"
    )


def test_data_dictionary_accordion_expandable(app_page: Page, base_url: str):
    """Verify that all 5 data dictionary accordion sections expand and display specs."""
    figures_page = FiguresPage(app_page, base_url)
    figures_page.navigate_to_dictionary()

    # Verify 5 specifications badge
    badge = app_page.locator("span:has-text('Table Specifications')").first
    assert "5 Table Specifications" in badge.inner_text()

    accordion_buttons = app_page.locator("#dictionaryAccordion .accordion-button")
    assert accordion_buttons.count() == 5, (
        f"Expected 5 accordion specifications, found {accordion_buttons.count()}"
    )

    expected_headers_per_section = [
        ["# up", "# down"],
        ["Study Type", "Variant Type", "Evidence from expression studies"],
        ["Tissue Type", "Tissue Subtype", "ASD Samples", "Control Samples"],
        ["ASD Susceptibility (SFARI)", "PubMed Reference"],
        ["Term ID", "Term Name", "Adjusted P-Value", "Overlap (k/N)", "Term Size"],
    ]

    # Verify each accordion section expands and shows its matching headers
    for i in range(5):
        btn = accordion_buttons.nth(i)
        btn.scroll_into_view_if_needed()
        if btn.get_attribute("aria-expanded") != "true":
            btn.click()
            app_page.wait_for_timeout(300)

        collapse = app_page.locator("#dictionaryAccordion .accordion-collapse").nth(i)
        assert collapse.is_visible(), f"Accordion section {i + 1} failed to expand"
        collapse_text = collapse.inner_text()
        for header in expected_headers_per_section[i]:
            assert header in collapse_text, (
                f"Header '{header}' missing from section {i + 1}"
            )


def test_help_tab_methodologies_and_diagnostic_tables(app_page: Page, base_url: str):
    """Verify that Experimental Methodologies and Diagnostic Tools tables are rendered and filterable in the Help tab."""
    figures_page = FiguresPage(app_page, base_url)
    figures_page.navigate_to_dictionary()

    app_page.wait_for_selector("#section-methods", state="visible")
    app_page.wait_for_selector("#section-diagnostic-tools", state="visible")

    # 1. Verify Methodologies table has 10 rows
    method_rows = app_page.locator("#methods-help-table tbody tr")
    assert method_rows.count() == 10

    # Test live filter on Methodologies search
    search_methods = app_page.locator("#methods-help-search")
    search_methods.fill("sequencing")
    app_page.wait_for_timeout(200)
    visible_methods = app_page.locator("#methods-help-table tbody tr:visible")
    assert 0 < visible_methods.count() < 10

    # Clear search
    search_methods.fill("")
    app_page.wait_for_timeout(200)
    assert app_page.locator("#methods-help-table tbody tr:visible").count() == 10

    # 2. Verify Diagnostic Tools table has 9 rows
    diag_rows = app_page.locator("#diagnostic-tools-help-table tbody tr")
    assert diag_rows.count() == 9

    # Test live filter on Diagnostic Tools search
    search_diag = app_page.locator("#diagnostic-tools-help-search")
    search_diag.fill("DSM")
    app_page.wait_for_timeout(200)
    visible_diag = app_page.locator("#diagnostic-tools-help-table tbody tr:visible")
    assert visible_diag.count() == 3

    # Clear search
    search_diag.fill("")
    app_page.wait_for_timeout(200)
    assert (
        app_page.locator("#diagnostic-tools-help-table tbody tr:visible").count() == 9
    )
