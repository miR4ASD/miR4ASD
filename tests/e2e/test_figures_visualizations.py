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
    figures_page.navigate_to_figures()

    # Verify 5 specifications badge
    badge = app_page.locator("span:has-text('Table Specifications')").first
    assert "5 Table Specifications" in badge.inner_text()

    accordion_buttons = app_page.locator("#dictionaryAccordion .accordion-button")
    assert accordion_buttons.count() == 5, (
        f"Expected 5 accordion specifications, found {accordion_buttons.count()}"
    )

    expected_headers_per_section = [
        ["Number of studies (Upregulated)", "Number of studies (Downregulated)"],
        ["Alteration", "Study description"],
        ["ASD Susceptibility (SFARI)", "PubMed Reference"],
        ["Tissue Type", "Tissue Subtype", "ASD Samples", "Control Samples"],
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
