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
    """Verify that data dictionary accordion sections expand and display definitions."""
    figures_page = FiguresPage(app_page, base_url)
    figures_page.navigate_to_figures()

    # Click first accordion button
    first_accordion = app_page.locator("#dictionaryAccordion .accordion-button").first
    first_accordion.scroll_into_view_if_needed()
    if first_accordion.get_attribute("aria-expanded") != "true":
        first_accordion.click()
        app_page.wait_for_timeout(300)

    # First accordion collapse body should now be visible
    first_body = app_page.locator("#dictionaryAccordion .accordion-collapse").first
    assert first_body.is_visible(), "Data dictionary accordion section failed to expand"
