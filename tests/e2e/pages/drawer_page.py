"""Page Object for Slide-Over Advanced Filter Drawer."""

from playwright.sync_api import Page

from tests.e2e.pages.base_page import BasePage


class DrawerPage(BasePage):
    """Encapsulates interactions with the slide-over filter drawer."""

    def __init__(self, page: Page, base_url: str):
        """Initialize DrawerPage."""
        super().__init__(page, base_url)

    def open_drawer(self) -> None:
        """Open drawer using visible filter toggle button."""
        self.open_filter_drawer()

    def close_drawer_via_icon(self) -> None:
        """Close drawer by clicking close 'X' button in header."""
        self.page.locator("#closeFilterDrawer").click()
        self.page.wait_for_timeout(400)

    def close_drawer_via_apply_button(self) -> None:
        """Close drawer by clicking 'Apply & Close' footer button."""
        self.page.locator("#closeFilterDrawerBtn").click()
        self.page.wait_for_timeout(400)

    def close_drawer_via_backdrop(self) -> None:
        """Close drawer by clicking backdrop overlay."""
        self.page.locator("#drawerBackdrop").click(position={"x": 10, "y": 10})
        self.page.wait_for_timeout(400)

    def is_drawer_open(self) -> bool:
        """Check if drawer is currently marked open and visible."""
        drawer = self.page.locator("#filterDrawer")
        classes = drawer.get_attribute("class") or ""
        return "open" in classes

    def set_search_mode(self, mode: str) -> None:
        """
        Switch shared search mode tab in drawer.

        Args:
            mode: One of 'mature', 'hairpin', 'gene'.
        """
        tab_id = f"#tab-mode-{mode}"
        self.page.locator(tab_id).click()
        self.page.wait_for_timeout(300)

    def enter_search_text(self, mode: str, text: str) -> None:
        """
        Enter query text in corresponding search mode textarea.

        Args:
            mode: One of 'mature', 'hairpin', 'gene'.
            text: Query string.
        """
        textarea_map = {
            "mature": "#filter-mature-id",
            "hairpin": "#filter-mirna-id",
            "gene": "#filter-target-gene",
        }
        selector = textarea_map.get(mode, "#filter-mature-id")
        self.page.locator(selector).fill(text)
        self.page.wait_for_timeout(400)

    def select_sfari_category(self, value: str) -> None:
        """
        Select SFARI ASD Susceptibility Category filter.

        Args:
            value: Option value to select.
        """
        self.page.locator("#filter-sfari-category").select_option(value)
        self.page.wait_for_timeout(400)

    def select_evidence_level(self, value: str) -> None:
        """
        Select Evidence Level filter.

        Args:
            value: Option value to select.
        """
        self.page.locator("#filter-evidence-level").select_option(value)
        self.page.wait_for_timeout(400)

    def select_expression_change(self, value: str) -> None:
        """
        Select Expression Change filter.

        Args:
            value: Option value to select.
        """
        self.page.locator("#filter-expression-change").select_option(value)
        self.page.wait_for_timeout(400)

    def select_genetic_alteration(self, value: str) -> None:
        """
        Select Genetic Variant/Alteration filter.

        Args:
            value: Option value to select.
        """
        self.page.locator("#filter-genetic-alteration").select_option(value)
        self.page.wait_for_timeout(400)

    def click_reset_filters_header(self) -> None:
        """Click 'Reset' link in drawer header."""
        self.page.locator("#drawer-btn-reset-filters").click()
        self.page.wait_for_timeout(400)

    def click_clear_all_footer(self) -> None:
        """Click 'Clear All' button in drawer footer."""
        self.page.locator("#resetFilters").click()
        self.page.wait_for_timeout(400)

    def click_deselect_header(self) -> None:
        """Click 'Deselect' link in drawer header."""
        self.page.locator("#drawer-btn-clear-selection").click()
        self.page.wait_for_timeout(400)

    def click_drawer_enrich_button(self) -> None:
        """Click 'Run Target Enrichment on Filtered miRNAs' CTA button."""
        self.page.locator("#drawer-btn-enrich").click()
        self.page.wait_for_timeout(600)

    def get_filter_count_badge_text(self) -> str:
        """Return text of drawer active filter count badge."""
        return self.page.locator("#drawer-filter-count-badge").inner_text().strip()

    def get_selection_badge_text(self) -> str:
        """Return text of drawer selection badge."""
        return self.page.locator("#drawer-selection-badge").inner_text().strip()

    def set_target_scope(self, scope: str) -> None:
        """
        Click target scope fast filter button in drawer.

        Args:
            scope: One of 'all', 'strong', 'sfari', 'sfari-cat1', 'brain',
                   'upregulated', 'downregulated'.
        """
        label = self.page.locator(f"label[for='drawer-scope-{scope}']")
        label.click()
        self.page.wait_for_timeout(400)

    def is_scope_selected(self, scope: str) -> bool:
        """
        Check if target scope radio in drawer is checked.

        Args:
            scope: Scope identifier string.
        """
        return self.page.locator(f"#drawer-scope-{scope}").is_checked()
