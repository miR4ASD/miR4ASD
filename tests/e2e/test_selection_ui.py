"""
End-to-end tests for the selection-driven UI:

- Per-tab filter cards are collapsed by default and expand via the header toggle.
- Selecting miRNAs auto-scopes the Target Genes table to those miRNAs' interactions
  (the "selected miRNAs" fields on the Targets + Enrichment tabs populate).
- Per-table "Selected only" toggles mirror the selection in the studies tables.
- Pasting miRNA IDs into a field adds them to the global selection; Copy and Clear work.
"""

import re

from playwright.sync_api import Page

from tests.e2e.pages.enrichment_page import EnrichmentPage
from tests.e2e.pages.expression_page import ExpressionPage
from tests.e2e.pages.genetic_page import GeneticPage
from tests.e2e.pages.targets_page import TargetsPage

FULL_INTERACTIONS = 17150


def _digits(text: str) -> int:
    """Parse an integer out of comma-formatted badge text (e.g. '2,995' -> 2995)."""
    d = re.sub(r"\D", "", text)
    return int(d) if d else 0


def _wait_info_entries(page: Page, table_id: str, mode: str, full: int = 0) -> None:
    """
    Wait until the table's info-string entry count satisfies ``mode``.

    Args:
        page: Playwright page.
        table_id: DataTable element id (e.g. 'targets-table').
        mode: 'less' waits for count < full; 'equal' waits for count == full.
        full: The full catalog count (for 'less').
    """
    predicate = (
        """(o) => {
            const el = document.getElementById(o.table + '_info');
            if (!el) return false;
            const m = el.textContent.match(/of ([\\d,]+) entries/);
            if (!m) return false;
            const c = parseInt(m[1].replace(/,/g, ''), 10);
            if (o.mode === 'equal') return c === o.full;
            return c < o.full;
        }"""
    )
    arg = {"table": table_id, "mode": mode, "full": full}
    # Poll via evaluate rather than wait_for_function: its rAF/timer polling is
    # throttled in headless when the page isn't actively painting, which made it
    # time out even after the condition was already satisfied.
    for _ in range(60):  # ~15s at 250ms intervals
        if page.evaluate(predicate, arg):
            break
        page.wait_for_timeout(250)
    else:
        last = page.evaluate(
            "(o) => (document.getElementById(o.table + '_info')||{}).textContent||''",
            arg,
        )
        raise TimeoutError(
            f"Timed out waiting for {table_id} info count to be '{mode}' {full} "
            f"(last: {last!r})"
        )
    page.wait_for_timeout(400)


def _expr_mature_ids(page: Page, limit: int = 1) -> list:
    """Read the first N mature miRNA ids from the expression table's checkboxes."""
    return page.evaluate(
        """(n) => {
            const rows = [...document.querySelectorAll(
                '#expression-table tbody tr input.expr-row-check')];
            return rows.slice(0, n)
                .map(cb => cb.getAttribute('data-mature') || '').filter(Boolean);
        }""",
        limit,
    )


def test_filter_cards_collapsed_by_default_and_toggle(
    app_page: Page, base_url: str
) -> None:
    """Per-tab filter cards collapse by default; the header toggle reveals inputs."""
    expr_page = ExpressionPage(app_page, base_url)
    gen_page = GeneticPage(app_page, base_url)
    targets_page = TargetsPage(app_page, base_url)

    # All three filter cards start collapsed (inputs hidden).
    expr_page.navigate_to_expression()
    assert expr_page.is_filters_collapsed(), (
        "Expression filters should be collapsed by default"
    )

    gen_page.navigate_to_genetic()
    assert gen_page.is_filters_collapsed(), (
        "Genetic filters should be collapsed by default"
    )

    targets_page.navigate_to_targets()
    assert targets_page.is_filters_collapsed(), (
        "Targets filters should be collapsed by default"
    )


def test_filter_card_toggle_reveals_and_rehides(
    app_page: Page, base_url: str
) -> None:
    """The header 'Filters' toggle expands the card, then collapses it again."""
    expr_page = ExpressionPage(app_page, base_url)
    expr_page.navigate_to_expression()

    assert expr_page.is_filters_collapsed()
    expr_page.toggle_filters()
    assert not expr_page.is_filters_collapsed(), (
        "Filters should be visible after toggle"
    )

    expr_page.toggle_filters()
    assert expr_page.is_filters_collapsed(), (
        "Filters should be hidden after second toggle"
    )


def test_filter_cards_independent_per_tab(app_page: Page, base_url: str) -> None:
    """Expanding one tab's filter card does not expand the other tabs' cards."""
    expr_page = ExpressionPage(app_page, base_url)
    gen_page = GeneticPage(app_page, base_url)

    expr_page.navigate_to_expression()
    assert expr_page.is_filters_collapsed()
    expr_page.toggle_filters()
    assert not expr_page.is_filters_collapsed()

    # The genetic card remains collapsed despite the expression card being open.
    gen_page.navigate_to_genetic()
    assert gen_page.is_filters_collapsed(), (
        "Genetic filters must stay collapsed independently"
    )


def test_selection_scopes_targets_view_modes(app_page: Page, base_url: str) -> None:
    """Selecting a miRNA auto-scopes the targets table; view modes switch it."""
    expr_page = ExpressionPage(app_page, base_url)
    targets_page = TargetsPage(app_page, base_url)
    targets_page.navigate_to_targets()
    assert _digits(targets_page.get_active_count_text()) == FULL_INTERACTIONS

    # Selecting a miRNA auto-scopes the targets table to its interactions.
    expr_page.navigate_to_expression()
    expr_page.select_row_by_index(0)
    targets_page.navigate_to_targets()
    _wait_info_entries(app_page, "targets-table", "less", FULL_INTERACTIONS)
    assert targets_page.get_active_view_mode() == "selected-mirna", (
        "Selecting a miRNA should default the targets table to the "
        "selected-miRNA view"
    )
    scoped = targets_page.get_filtered_total()
    assert 0 < scoped < FULL_INTERACTIONS, (
        f"Targets should be scoped to a subset ({scoped} < {FULL_INTERACTIONS})"
    )

    # The "All" view reveals the full interaction catalog.
    targets_page.set_view_mode("all")
    _wait_info_entries(app_page, "targets-table", "equal", FULL_INTERACTIONS)
    assert targets_page.get_filtered_total() == FULL_INTERACTIONS, (
        "The 'All' view should reveal the full interaction catalog"
    )
    assert _digits(targets_page.get_active_genes_count_text()) == 2995
    assert targets_page.get_active_view_mode() == "all"

    # Returning to "Selected miRNAs" restores the scoped subset.
    targets_page.set_view_mode("selected-mirna")
    _wait_info_entries(app_page, "targets-table", "less", FULL_INTERACTIONS)
    assert targets_page.get_filtered_total() == scoped, (
        "The 'Selected miRNAs' view should restore the scoped subset"
    )
    assert targets_page.get_active_view_mode() == "selected-mirna"


def test_selected_only_toggles_studies_tables(app_page: Page, base_url: str) -> None:
    """Per-table 'Selected only' mirrors the miRNA selection in the studies tables."""
    expr_page = ExpressionPage(app_page, base_url)
    gen_page = GeneticPage(app_page, base_url)

    expr_page.navigate_to_expression()
    full = expr_page.get_filtered_total()
    assert full > 0

    # No selection yet: the 'Selected only' toggle is disabled.
    assert not expr_page.is_show_selected_only_enabled()

    expr_page.select_row_by_index(0)
    assert expr_page.is_show_selected_only_enabled(), (
        "Toggle must enable once a miRNA is selected"
    )

    expr_page.toggle_show_selected_only()
    assert expr_page.is_show_selected_only_active(), (
        "Toggle should enter its active state"
    )
    only_selected = expr_page.get_filtered_total()
    assert 1 <= only_selected < full, (
        f"'Selected only' should show a strict subset ({only_selected} < {full})"
    )

    # Toggling off restores the full set.
    expr_page.toggle_show_selected_only()
    assert not expr_page.is_show_selected_only_active()
    assert expr_page.get_filtered_total() == full

    # The genetic card exposes the same capability. A global selection already
    # exists (expression row 0), so the genetic "Selected only" toggle is
    # enabled. Selecting the genetic row and toggling mirrors the selection.
    gen_page.navigate_to_genetic()
    gen_page.select_row_by_index(0)
    assert gen_page.is_show_selected_only_enabled(), (
        "Genetic toggle must be enabled because a miRNA is selected"
    )
    gen_page.toggle_show_selected_only()
    assert gen_page.is_show_selected_only_active()


def test_selection_populates_mirna_fields(app_page: Page, base_url: str) -> None:
    """Selecting a miRNA populates the fields on the Targets + Enrichment tabs."""
    expr_page = ExpressionPage(app_page, base_url)
    targets_page = TargetsPage(app_page, base_url)
    enrichment_page = EnrichmentPage(app_page, base_url)

    expr_page.navigate_to_expression()
    expr_page.select_row_by_index(0)

    # Both the targets field and the enrichment field reflect the selection.
    targets_page.navigate_to_targets()
    assert targets_page.get_selected_mirna_count() == 1
    assert len(targets_page.get_selected_mirna_chips()) == 1

    enrichment_page.navigate_to_enrichment()
    assert enrichment_page.get_selected_mirna_count() == 1
    assert len(enrichment_page.get_selected_mirna_chips()) == 1


def test_paste_mirna_ids_into_field(app_page: Page, base_url: str) -> None:
    """Pasting a known miRNA ID into a field adds it to the global selection."""
    expr_page = ExpressionPage(app_page, base_url)
    expr_page.navigate_to_expression()
    mature = _expr_mature_ids(app_page, 1)
    assert mature, "Expected a mature miRNA id on the first expression row"

    enrichment_page = EnrichmentPage(app_page, base_url)
    enrichment_page.navigate_to_enrichment()
    assert enrichment_page.get_selected_mirna_count() == 0

    # Paste the mature id (debounced parse) — the selection should grow.
    enrichment_page.fill_enrichment_mirna_input(mature[0])
    assert enrichment_page.get_selected_mirna_count() >= 1, (
        "Pasting a known miRNA id should add it to the selection"
    )

    # The global selection now drives the targets view mode.
    targets_page = TargetsPage(app_page, base_url)
    targets_page.navigate_to_targets()
    assert targets_page.get_active_view_mode() == "selected-mirna", (
        "The targets table should default to the selected-miRNA view "
        "after a paste-driven selection"
    )
    assert targets_page.get_selected_mirna_count() >= 1


def test_copy_and_clear_mirna_field(app_page: Page, base_url: str) -> None:
    """Copy writes the selected miRNA ids to the clipboard; Clear empties it."""
    # Derive two DISTINCT mature ids so the pasted selection is exactly two entries.
    expr_page = ExpressionPage(app_page, base_url)
    expr_page.navigate_to_expression()
    pool = _expr_mature_ids(app_page, 12)
    distinct = []
    for m in pool:
        if m and m not in distinct:
            distinct.append(m)
    assert len(distinct) >= 2, f"Need two distinct miRNA ids, got {distinct}"
    a, b = distinct[0], distinct[1]
    expected_copy = ", ".join(sorted([a, b]))

    enrichment_page = EnrichmentPage(app_page, base_url)
    enrichment_page.navigate_to_enrichment()
    enrichment_page.fill_enrichment_mirna_input(f"{a} {b}")
    n_selected = enrichment_page.get_selected_mirna_count()
    assert n_selected == 2, (
        f"Expected exactly 2 selected miRNAs, got {n_selected}"
    )

    targets_page = TargetsPage(app_page, base_url)
    targets_page.navigate_to_targets()
    assert targets_page.get_selected_mirna_count() == 2

    targets_page.click_copy_targets_mirnas()
    clipboard = app_page.evaluate("async () => navigator.clipboard.readText()")
    assert clipboard.strip() == expected_copy, (
        f"Clipboard should hold the selected miRNA ids: "
        f"{clipboard!r} != {expected_copy!r}"
    )

    # Clear empties the selection and the targets field.
    targets_page.click_clear_targets_mirnas()
    assert targets_page.get_selected_mirna_count() == 0
    assert not targets_page.get_selected_mirna_chips(), (
        "Chips should be empty after Clear"
    )
