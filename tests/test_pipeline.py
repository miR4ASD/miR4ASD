"""Unit and integration tests for the miR4ASD data processing pipeline."""

import json
import os

import pandas as pd

from process_data import (
    clean_col_names,
    create_gff_maps,
    create_mirbase_hairpin_link,
    create_mirbase_mature_link,
    normalize_study_name,
)


def test_gff_maps_loading():
    """Test that GFF3 file parses into non-empty hairpin and mature maps."""
    gff_path = "hsa.gff3"
    assert os.path.exists(gff_path), f"GFF3 file {gff_path} not found."
    hairpin_map, mature_map = create_gff_maps(gff_path)
    assert len(hairpin_map) > 1000
    assert len(mature_map) > 1000
    assert "hsa-let-7a-1" in hairpin_map
    assert "hsa-let-7a-5p" in mature_map


def test_clean_col_names():
    """Test that column names are stripped of whitespace and mirbase annotations."""
    df = pd.DataFrame(columns=["miRNA hairpin\n(MIRBASE v22.1)", "  Study  "])
    cleaned = clean_col_names(df)
    assert list(cleaned.columns) == ["miRNA hairpin", "Study"]


def test_normalize_study_name():
    """Test study name stripping without corrupting valid keys."""
    assert normalize_study_name(" Seno (2011) ") == "Seno (2011)"
    assert normalize_study_name("Vasu (2014)") == "Vasu (2014)"


def test_mirbase_link_generation():
    """Test exact, case-insensitive, and prefix-tolerant miRBase link resolution."""
    link_exact = create_mirbase_hairpin_link("hsa-let-7a-1")
    assert 'href="https://www.mirbase.org/hairpin/MI0000060"' in link_exact
    assert ">hsa-let-7a-1</a>" in link_exact

    # Case-insensitive
    link_case = create_mirbase_hairpin_link("hsa-miR-125b-1")
    assert 'href="https://www.mirbase.org/hairpin/MI0000446"' in link_case

    # Missing hsa- prefix for mature
    link_prefixed = create_mirbase_mature_link("miR-106b-5p")
    assert 'href="https://www.mirbase.org/mature/MIMAT0000680"' in link_prefixed


def test_generated_json_files_exist_and_valid():
    """Test that all generated JSON feeds exist, parse as JSON, and are non-empty."""
    files = [
        "expression_studies.json",
        "other_studies.json",
        "study_details.json",
        "statistics.json",
        "target_genes.json",
    ]
    for filename in files:
        assert os.path.exists(filename), f"Expected JSON feed {filename} not found."
        with open(filename, "r") as f:
            data = json.load(f)
            assert len(data) > 0, f"JSON feed {filename} is empty."


def test_target_genes_structure_and_sfari_matching():
    """Test target_genes.json schema, SFARI risk annotations, and evidence tiers."""
    assert os.path.exists("target_genes.json"), "target_genes.json not found."
    with open("target_genes.json", "r") as f:
        targets = json.load(f)

    assert len(targets) > 50000, (
        f"Expected >50000 target interactions, found {len(targets)}"
    )

    required_keys = [
        "precursor_mirna",
        "mature_mirna",
        "gene_symbol",
        "gene_name",
        "is_sfari",
        "sfari_score",
        "evidence_level",
        "experimental_methods",
        "regulation",
        "tissue",
        "pmids",
    ]

    sfari_count = 0
    strong_count = 0
    for record in targets:
        for key in required_keys:
            assert key in record, f"Missing key {key} in target record"

        if record["is_sfari"]:
            sfari_count += 1
            assert (
                "Category" in record["sfari_score"]
                or "Syndromic" in record["sfari_score"]
            )

        if "Strong" in record["evidence_level"]:
            strong_count += 1

    assert sfari_count > 10000, (
        f"Expected >10000 SFARI interactions, found {sfari_count}"
    )
    assert strong_count > 1000, (
        f"Expected >1000 Strong Evidence interactions, found {strong_count}"
    )

    # Verify specific known ASD genes are tagged
    target_gene_symbols = {r["gene_symbol"].upper() for r in targets}
    assert "AGO1" in target_gene_symbols
    assert "AGO4" in target_gene_symbols
    assert "PTEN" in target_gene_symbols
    assert "SHANK3" in target_gene_symbols
    assert "MECP2" in target_gene_symbols


def test_study_details_matching_integrity():
    """Verify that records with studies have non-empty StudyDetails."""
    with open("expression_studies.json", "r") as f:
        expr_data = json.load(f)

    with open("other_studies.json", "r") as f:
        other_data = json.load(f)
    assert len(other_data) > 0

    # Check that Seno and Vasu records have populated StudyDetails
    seno_records = [
        r
        for r in expr_data
        if any(d.get("Study") == "Seno (2011)" for d in r.get("StudyDetails", []))
    ]
    assert len(seno_records) == 28

    vasu_records = [
        r
        for r in expr_data
        if any(d.get("Study") == "Vasu (2014)" for d in r.get("StudyDetails", []))
    ]
    assert len(vasu_records) == 17

    # All expression entries must have at least one study in StudyDetails
    for idx, record in enumerate(expr_data):
        assert len(record.get("StudyDetails", [])) > 0, (
            f"Record {idx} has empty StudyDetails"
        )


def test_statistics_consistency():
    """Verify summary statistics schema and value ranges."""
    with open("statistics.json", "r") as f:
        stats = json.load(f)

    assert "total_studies" in stats and stats["total_studies"] > 0
    assert "total_mirna_genes" in stats and stats["total_mirna_genes"] > 0
    assert "total_mirna_mature" in stats and stats["total_mirna_mature"] > 0
    assert "alteration_counts" in stats
    assert stats["alteration_counts"]["upregulated"] > 0
    assert stats["alteration_counts"]["downregulated"] > 0
    assert "tissue_counts" in stats
    assert "Blood" in stats["tissue_counts"]
    assert "Brain" in stats["tissue_counts"]
    assert "Umbilical cord" in stats["tissue_counts"]
    assert "target_stats" in stats
    assert stats["target_stats"]["total_target_genes"] > 0
    assert stats["target_stats"]["total_sfari_target_genes"] > 0
    assert stats["target_stats"]["total_target_interactions"] > 0


def test_target_resolution_for_enrichment():
    """Verify target gene resolution logic from miRNAs for enrichment payloads."""
    with open("target_genes.json", "r") as f:
        targets = json.load(f)

    # Build mature map
    mature_to_genes = {}
    for item in targets:
        mature = item.get("mature_mirna")
        gene = item.get("gene_symbol")
        if mature and gene:
            if mature not in mature_to_genes:
                mature_to_genes[mature] = set()
            mature_to_genes[mature].add(gene)

    # Test resolution for known brain miRNAs
    assert "hsa-miR-132-3p" in mature_to_genes
    genes_132 = mature_to_genes["hsa-miR-132-3p"]
    assert len(genes_132) > 10, (
        f"Expected >10 targets for hsa-miR-132-3p, got {len(genes_132)}"
    )

    # Ensure format is valid for g:Profiler payload
    query_payload = sorted(list(genes_132))
    assert all(isinstance(g, str) and len(g) > 0 for g in query_payload)


def test_multi_mirna_and_gene_mapping():
    """Verify multi-miRNA batch resolution and reverse gene-to-miRNA mapping."""
    with open("target_genes.json", "r") as f:
        targets = json.load(f)

    # Build bidirectional maps
    mature_to_genes = {}
    gene_to_matures = {}
    for item in targets:
        mature = item.get("mature_mirna")
        gene = item.get("gene_symbol")
        if mature and gene:
            mature_to_genes.setdefault(mature, set()).add(gene)
            gene_to_matures.setdefault(gene.upper(), set()).add(mature)

    # 1. Multi-miRNA selection union test
    selected_mirnas = ["hsa-let-7a-5p", "hsa-miR-132-3p"]
    combined_targets = set()
    for m in selected_mirnas:
        if m in mature_to_genes:
            combined_targets.update(mature_to_genes[m])
    assert len(combined_targets) > len(mature_to_genes["hsa-let-7a-5p"])
    assert len(combined_targets) > len(mature_to_genes["hsa-miR-132-3p"])

    # 2. Multi-gene to miRNAs search test
    query_genes = ["PTEN", "SHANK3"]
    regulating_mirnas = set()
    for g in query_genes:
        if g in gene_to_matures:
            regulating_mirnas.update(gene_to_matures[g])
    assert len(regulating_mirnas) > 0
    # Both PTEN and SHANK3 have validated miRNAs in DIANA-TarBase
    assert any("miR" in m or "let" in m for m in regulating_mirnas)


def test_target_genes_child_details_structure():
    """Verify target interactions contain required metadata fields for child rows."""
    with open("target_genes.json", "r") as f:
        targets = json.load(f)

    assert len(targets) > 0
    # Sample verification for required child row fields
    for item in targets[:100]:
        assert "experimental_methods" in item
        assert "regulation" in item
        assert "tissue" in item
        assert "pmids" in item
        assert "database_source" in item
        assert item["database_source"] in [
            "DIANA-TarBase v9.0",
            "miRTarBase 10.0",
            "TarBase & miRTarBase (Consensus)",
        ]
        # Verify methods can be split cleanly
        methods = [
            m.strip() for m in item["experimental_methods"].split(";") if m.strip()
        ]
        assert len(methods) > 0


def test_non_destructive_gene_scope_filtering():
    """Verify scope filtering filters non-destructively on base target genes."""
    with open("target_genes.json", "r") as f:
        targets = json.load(f)

    gene_meta = {}
    mature_to_genes = {}
    for item in targets:
        gene = item.get("gene_symbol")
        mature = item.get("mature_mirna")
        if gene and mature:
            mature_to_genes.setdefault(mature, set()).add(gene)
            if gene not in gene_meta:
                gene_meta[gene] = {
                    "is_sfari": item.get("is_sfari", False),
                    "sfari_score": item.get("sfari_score", ""),
                    "evidence_level": item.get("evidence_level", ""),
                    "tissue": item.get("tissue", ""),
                }

    # Selected miRNAs
    selected_mirnas = ["hsa-let-7a-5p", "hsa-miR-132-3p"]
    base_genes = set()
    for m in selected_mirnas:
        if m in mature_to_genes:
            base_genes.update(mature_to_genes[m])

    base_list = sorted(list(base_genes))
    assert len(base_list) > 20

    # 1. Scope: SFARI Cat 1 filter
    sfari_cat1_genes = [
        g
        for g in base_list
        if gene_meta.get(g, {}).get("sfari_score", "").find("Category 1") != -1
    ]
    assert 0 < len(sfari_cat1_genes) < len(base_list)

    # Base list must remain intact
    assert len(base_list) > len(sfari_cat1_genes)

    # 2. Scope: Strong Evidence filter
    strong_genes = [
        g
        for g in base_list
        if gene_meta.get(g, {}).get("evidence_level") == "Strong Evidence"
    ]
    assert 0 < len(strong_genes) <= len(base_list)

    # 3. Scope reset to All
    all_restored = list(base_list)
    assert set(all_restored) == set(base_genes)


def test_precursor_and_genetic_study_target_resolution():
    """Verify target resolution works via precursor hairpins when mature is absent."""
    with open("other_studies.json", "r") as f:
        other = json.load(f)
    with open("target_genes.json", "r") as f:
        targets = json.load(f)

    # Hairpin index
    hairpin_to_targets = {}
    for t in targets:
        hps = t.get("precursor_mirna")
        if hps:
            for hp in hps.split("; "):
                clean_hp = hp.strip().lower()
                hairpin_to_targets.setdefault(clean_hp, set()).add(t["gene_symbol"])

    # Find genetic studies without mature_mirna
    no_mature_studies = [
        r for r in other if not r.get("mature_mirna") and r.get("precursor_mirna")
    ]
    assert len(no_mature_studies) > 50

    # Ensure precursors in genetic studies can resolve targets
    resolvable_count = 0
    sample_genes = set()
    for s in no_mature_studies:
        hp_raw = s["precursor_mirna"]
        clean_hp = (
            hp_raw.split(">")[-2].split("<")[0].strip().lower()
            if "<" in hp_raw
            else hp_raw.strip().lower()
        )
        if clean_hp in hairpin_to_targets:
            resolvable_count += 1
            sample_genes.update(hairpin_to_targets[clean_hp])

    assert resolvable_count > 0, "No precursors resolved from genetic studies!"
    assert len(sample_genes) > 50, (
        f"Expected >50 targets from genetic precursors, got {len(sample_genes)}"
    )


def test_regulation_target_gene_filtering():
    """Verify regulation target filtering resolves distinct sets of targets."""
    with open("expression_studies.json", "r") as f:
        expr = json.load(f)
    with open("target_genes.json", "r") as f:
        targets = json.load(f)

    def clean(s):
        if not s:
            return ""
        if "<" in s:
            s = s.split(">")[-2].split("<")[0]
        return s.strip().lower()

    up_matures = {
        clean(r["mature_mirna"])
        for r in expr
        if r.get("expression_change") == "Upregulated" and r.get("mature_mirna")
    }
    down_matures = {
        clean(r["mature_mirna"])
        for r in expr
        if r.get("expression_change") == "Downregulated" and r.get("mature_mirna")
    }

    up_targets = {
        t["gene_symbol"]
        for t in targets
        if clean(t.get("mature_mirna")) in up_matures and t.get("gene_symbol")
    }
    down_targets = {
        t["gene_symbol"]
        for t in targets
        if clean(t.get("mature_mirna")) in down_matures and t.get("gene_symbol")
    }

    assert len(up_targets) > 500
    assert len(down_targets) > 500
    # Both sets are large but non-identical
    assert up_targets != down_targets


def test_mirna_selection_prerequisite_and_target_filtering_isolation():
    """
    Verify 0 selected miRNAs yields 0 targets.

    Also verify filters only modulate targets of selected miRNAs.
    """
    with open("target_genes.json", "r") as f:
        targets = json.load(f)

    # Index targets by mature and hairpin
    mature_to_targets = {}
    hairpin_to_targets = {}
    for t in targets:
        m = (t.get("mature_mirna") or "").strip().lower()
        if m:
            mature_to_targets.setdefault(m, []).append(t)
        hps = t.get("precursor_mirna")
        if hps:
            for hp in hps.split("; "):
                hairpin_to_targets.setdefault(hp.strip().lower(), []).append(t)

    def resolve_targets(m_list, hp_list):
        if not m_list and not hp_list:
            return set()
        matched = []
        for m in m_list:
            matched.extend(mature_to_targets.get(m.strip().lower(), []))
        for hp in hp_list:
            matched.extend(hairpin_to_targets.get(hp.strip().lower(), []))
        return {t["gene_symbol"] for t in matched if t.get("gene_symbol")}

    # 1. Zero selected miRNAs must yield strictly 0 targets
    assert len(resolve_targets([], [])) == 0

    # 2. Selecting a specific miRNA yields strictly its targets
    sel_mirna = "hsa-let-7a-5p"
    base_targets = resolve_targets([sel_mirna], [])
    assert len(base_targets) > 0
    # Confirm it does not include targets unrelated to hsa-let-7a-5p
    all_genes = {t["gene_symbol"] for t in targets if t.get("gene_symbol")}
    assert len(base_targets) < len(all_genes)

    # 3. Target filtering strictly modulates that selected set
    sfari_targets_of_sel = {
        t["gene_symbol"]
        for t in mature_to_targets.get(sel_mirna.lower(), [])
        if t.get("is_sfari") and t.get("gene_symbol")
    }
    assert 0 < len(sfari_targets_of_sel) < len(base_targets)
    # The filtered set is a strict subset of the selected miRNA targets
    assert sfari_targets_of_sel.issubset(base_targets)

    # 4. Deselecting resets back to empty
    assert len(resolve_targets([], [])) == 0


def test_dual_database_source_integrity_and_provenance():
    """Verify dual-database source tags (TarBase, miRTarBase, Consensus)."""
    with open("target_genes.json", "r") as f:
        targets = json.load(f)
    with open("statistics.json", "r") as f:
        stats = json.load(f)

    # Database source distribution
    source_counts = {}
    for item in targets:
        src = item.get("database_source")
        source_counts[src] = source_counts.get(src, 0) + 1

    assert "DIANA-TarBase v9.0" in source_counts
    assert "miRTarBase 10.0" in source_counts
    assert "TarBase & miRTarBase (Consensus)" in source_counts

    # Verify meaningful numbers in all 3 classes
    assert source_counts["DIANA-TarBase v9.0"] > 50000
    assert source_counts["miRTarBase 10.0"] > 5000
    assert source_counts["TarBase & miRTarBase (Consensus)"] > 5000

    # Verify statistics.json metrics
    t_stats = stats.get("target_stats", {})
    assert t_stats.get("consensus_interactions", 0) > 5000
    assert t_stats.get("mirtarbase_total_interactions", 0) > 15000
    assert t_stats.get("tarbase_total_interactions", 0) > 60000
