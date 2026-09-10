"""End-to-end tests for global floating controls: Back-to-Top and Toast alerts."""

from playwright.sync_api import Page

from tests.e2e.pages.base_page import BasePage
from tests.e2e.pages.enrichment_page import EnrichmentPage


def test_back_to_top_button(app_page: Page, base_url: str):
    """Verify Back-to-Top button appears upon scrolling down and scrolls back to top."""
    base_page = BasePage(app_page, base_url)
    base_page.navigate()

    # Initially at top; back to top button should not have 'show' class
    btn = app_page.locator("#btn-back-to-top")
    assert "show" not in (btn.get_attribute("class") or "")

    # Scroll down window
    app_page.evaluate("window.scrollTo(0, 800); $(window).trigger('scroll');")
    app_page.wait_for_selector("#btn-back-to-top.show", timeout=5000)

    # Button should now be visible and have 'show' class
    assert "show" in (btn.get_attribute("class") or "")
    assert base_page.is_back_to_top_visible()

    # Click Back to Top
    base_page.click_back_to_top()
    app_page.wait_for_timeout(800)

    # Scroll position should return near top
    scroll_y = app_page.evaluate("window.scrollY || window.pageYOffset;")
    assert scroll_y < 100


def test_toast_dismiss_button(app_page: Page, base_url: str):
    """Verify warning toast can be dismissed via its close button."""
    enrichment_page = EnrichmentPage(app_page, base_url)
    enrichment_page.navigate_to_enrichment()

    # Trigger warning toast by calling window.showSelectionWarning
    app_page.evaluate(
        "window.showSelectionWarning && "
        "window.showSelectionWarning('Target genes required for test');"
    )
    app_page.wait_for_selector("#selectionWarningToast.show", timeout=5000)

    # Toast should be visible
    toast = app_page.locator("#selectionWarningToast")
    assert "show" in (toast.get_attribute("class") or "")

    # Dismiss toast
    enrichment_page.dismiss_toast()
    app_page.wait_for_timeout(400)
    assert "show" not in (toast.get_attribute("class") or "")
