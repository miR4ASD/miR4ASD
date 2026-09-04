"""Page Object for Database Statistics & Visualizations section."""

from typing import List, Tuple

from playwright.sync_api import Locator

from tests.e2e.pages.base_page import BasePage


class FiguresPage(BasePage):
    """Page component managing figure images, responsive grid, and modals."""

    def navigate_to_figures(self) -> None:
        """Navigate to the About tab and scroll to figures section."""
        self.switch_tab("about")
        heading = self.page.locator("h2:has-text('Database Statistics')")
        heading.scroll_into_view_if_needed()

    def get_figure_images(self) -> List[Locator]:
        """Return list of all figure image locators on page."""
        return self.page.locator(".figure-img").all()

    def get_image_natural_dimensions(self, locator: Locator) -> Tuple[int, int]:
        """
        Return natural width and height of an image element.

        Args:
            locator: Playwright Locator for the image.

        Returns:
            Tuple of (naturalWidth, naturalHeight).
        """
        w = locator.evaluate("el => el.naturalWidth")
        h = locator.evaluate("el => el.naturalHeight")
        return int(w), int(h)

    def click_figure_card(self, index: int = 0) -> None:
        """
        Click a figure card by index.

        Args:
            index: 0-based card index.
        """
        cards = self.page.locator(".figure-card").all()
        if index < len(cards):
            cards[index].click()
            self.page.wait_for_timeout(400)

    def is_modal_present_or_visible(self) -> bool:
        """Verify whether an image modal or backdrop exists or is visible."""
        modal = self.page.locator("#imageModal")
        backdrop = self.page.locator(".modal-backdrop")
        modal_vis = modal.is_visible() if modal.count() > 0 else False
        backdrop_vis = backdrop.is_visible() if backdrop.count() > 0 else False
        return modal_vis or backdrop_vis
