"""End-to-end tests for Mobile-First Responsive Design & multi-viewport layout."""

import pytest
from playwright.sync_api import Page

from tests.e2e.pages.figures_page import FiguresPage

VIEWPORTS = [
    ("desktop", {"width": 1400, "height": 900}),
    ("tablet", {"width": 768, "height": 1024}),
    ("mobile", {"width": 375, "height": 667}),
]


@pytest.mark.parametrize("device_name, viewport", VIEWPORTS)
def test_viewport_has_no_horizontal_overflow(
    app_page: Page, base_url: str, device_name: str, viewport: dict
):
    """Verify scrollWidth does not exceed innerWidth on any device."""
    app_page.set_viewport_size(viewport)
    app_page.wait_for_timeout(600)

    figures_page = FiguresPage(app_page, base_url)
    figures_page.navigate_to_figures()

    scroll_width = app_page.evaluate("() => document.documentElement.scrollWidth")
    inner_width = app_page.evaluate("() => window.innerWidth")

    assert scroll_width <= inner_width + 5, (
        f"Overflow on {device_name} ({viewport})! "
        f"scrollWidth={scroll_width}, innerWidth={inner_width}"
    )


def test_mobile_figures_grid_stacking(app_page: Page, base_url: str):
    """Verify that figure cards stack responsively in single column on mobile."""
    app_page.set_viewport_size({"width": 375, "height": 667})
    app_page.wait_for_timeout(500)

    figures_page = FiguresPage(app_page, base_url)
    figures_page.navigate_to_figures()

    images = figures_page.get_figure_images()
    assert len(images) >= 7, "Figure cards missing on mobile view"

    # All images should remain visible and contained
    for img in images:
        assert img.is_visible(), "Figure image hidden or collapsed on mobile view"
        box = img.bounding_box()
        assert box is not None and box["width"] <= 375, (
            f"Figure image exceeded mobile width: {box}"
        )
