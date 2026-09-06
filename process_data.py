import csv
import gzip
import json
import os
from typing import Any, Dict, List, Optional, Set, Tuple

import pandas as pd


def create_gff_maps(gff_file: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Parse a GFF3 file and create name-to-ID maps for miRNA hairpins and mature miRNAs.

    Parameters
    ----------
    gff_file : str
        The path to the GFF3 file.

    Returns
    -------
    Tuple[Dict[str, str], Dict[str, str]]
        (hairpin_map, mature_map) mapping names to miRBase IDs.
    """
    hairpin_map = {}
    mature_map = {}
    with open(gff_file, "r") as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split("\t")
            if len(parts) == 9:
                attributes = parts[8]
                attr_dict = {}
                for attr in attributes.split(";"):
                    if not attr:
                        continue
                    if "=" in attr:
                        key, value = attr.split("=", 1)
                        attr_dict[key.strip()] = value.strip()

                if parts[2] == "miRNA_primary_transcript":
                    if "Name" in attr_dict and "ID" in attr_dict:
                        hairpin_map[attr_dict["Name"]] = attr_dict["ID"]
                elif parts[2] == "miRNA":
                    if "Name" in attr_dict and "ID" in attr_dict:
                        mature_map[attr_dict["Name"]] = attr_dict["ID"]
    return hairpin_map, mature_map


def clean_col_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the column names of a DataFrame by stripping whitespace and extra text.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame whose columns should be cleaned.

    Returns
    -------
    pd.DataFrame
        The DataFrame with cleaned column names.
    """
    cols = df.columns
    new_cols = [col.replace("\n(MIRBASE v22.1)", "").strip() for col in cols]
    df.columns = new_cols
    return df


def normalize_study_name(name: Any) -> str:
    """
    Normalize study names to match keys in the study details sheet.

    Parameters
    ----------
    name : Any
        The raw study name.

    Returns
    -------
    str
        The normalized study name.
    """
    return str(name).strip()


_GFF_CACHE: Optional[
    Tuple[Dict[str, str], Dict[str, str], Dict[str, str], Dict[str, str]]
] = None


def get_gff_maps(
    gff_file: str = "hsa.gff3",
) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str], Dict[str, str]]:
    """
    Retrieve cached GFF3 maps or load if not initialized.

    Parameters
    ----------
    gff_file : str
        Path to the GFF3 annotation file.

    Returns
    -------
    Tuple[Dict[str, str], Dict[str, str], Dict[str, str], Dict[str, str]]
        (hairpin_to_id_map, mature_to_id_map, hairpin_lower_map, mature_lower_map)
    """
    global _GFF_CACHE
    if _GFF_CACHE is None:
        hairpin_map, mature_map = create_gff_maps(gff_file)
        hairpin_lower = {k.lower(): v for k, v in hairpin_map.items()}
        mature_lower = {k.lower(): v for k, v in mature_map.items()}
        _GFF_CACHE = (hairpin_map, mature_map, hairpin_lower, mature_lower)
    return _GFF_CACHE


def _create_mirbase_link(
    name: Any,
    entity_type: str,
    exact_map: Dict[str, str],
    lower_map: Dict[str, str],
) -> Any:
    """
    Generate an HTML anchor tag for a miRNA pointing to miRBase.

    Parameters
    ----------
    name : Any
        Name of the precursor or mature miRNA.
    entity_type : str
        Either 'hairpin' or 'mature'.
    exact_map : Dict[str, str]
        Case-sensitive mapping of name to miRBase accession ID.
    lower_map : Dict[str, str]
        Case-insensitive mapping of lowercase name to miRBase accession ID.

    Returns
    -------
    Any
        HTML anchor string with rel="noopener noreferrer" if mapped,
        otherwise original value.
    """
    if pd.isna(name):
        return name
    name_str = str(name).strip()
    if not name_str:
        return name

    mirbase_id = None
    if name_str in exact_map:
        mirbase_id = exact_map[name_str]
    else:
        name_lower = name_str.lower()
        if name_lower in lower_map:
            mirbase_id = lower_map[name_lower]
        elif not name_lower.startswith("hsa-"):
            prefixed = f"hsa-{name_lower}"
            if prefixed in lower_map:
                mirbase_id = lower_map[prefixed]

    if mirbase_id:
        return (
            f'<a href="https://www.mirbase.org/{entity_type}/{mirbase_id}" '
            f'target="_blank" rel="noopener noreferrer">{name_str}</a>'
        )

    return name_str


def create_mirbase_hairpin_link(hairpin_name: Any, gff_file: str = "hsa.gff3") -> Any:
    """
    Generate HTML anchor for hairpin miRNA pointing to miRBase.

    Parameters
    ----------
    hairpin_name : Any
        Name of the precursor miRNA hairpin.
    gff_file : str
        Path to the GFF3 file for ID resolution.

    Returns
    -------
    Any
        HTML anchor link or original string.
    """
    hairpin_map, _, hairpin_lower, _ = get_gff_maps(gff_file)
    return _create_mirbase_link(hairpin_name, "hairpin", hairpin_map, hairpin_lower)


def create_mirbase_mature_link(mature_name: Any, gff_file: str = "hsa.gff3") -> Any:
    """
    Generate HTML anchor for mature miRNA pointing to miRBase.

    Parameters
    ----------
    mature_name : Any
        Name of the mature miRNA.
    gff_file : str
        Path to the GFF3 file for ID resolution.

    Returns
    -------
    Any
        HTML anchor link or original string.
    """
    _, mature_map, _, mature_lower = get_gff_maps(gff_file)
    return _create_mirbase_link(mature_name, "mature", mature_map, mature_lower)


def parse_pmid(raw_val: Any) -> Optional[str]:
    """
    Parse and validate a PubMed ID into a clean numeric string.

    Parameters
    ----------
    raw_val : Any
        Raw value representing a PMID (string, float, int).

    Returns
    -------
    Optional[str]
        Clean string PMID (e.g. '30232454'), or None if invalid or zero.
    """
    if raw_val is None or pd.isna(raw_val):
        return None
    cleaned = str(raw_val).strip()
    if not cleaned or cleaned.lower() in ("nan", "none", "na", "0"):
        return None
    try:
        pmid_num = int(float(cleaned))
        if pmid_num > 0:
            return str(pmid_num)
    except (ValueError, TypeError, OverflowError):
        pass
    return None


def standardize_delimiters(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Standardize column delimiters from comma to semicolon.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to process.
    columns : List[str]
        List of column names to standardize.

    Returns
    -------
    pd.DataFrame
        DataFrame with standardized delimiters.
    """
    for col in columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r"\s*,\s*", "; ", regex=True)
    return df


def resolve_study_details(
    study_string: Any,
    study_details_map: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Resolve study names to their metadata records from a lookup map.

    Parameters
    ----------
    study_string : Any
        Semicolon-separated list of study names.
    study_details_map : Dict[str, Dict[str, Any]]
        Lookup dictionary mapping normalized study names to detail dicts.

    Returns
    -------
    List[Dict[str, Any]]
        List of matched study detail records.
    """
    if pd.isna(study_string):
        return []
    study_names = [s.strip() for s in str(study_string).split(";")]
    details_list = []
    for study_name in study_names:
        study_name_norm = normalize_study_name(study_name)
        if study_name_norm in study_details_map:
            details_list.append(study_details_map[study_name_norm])
    return details_list


# --- Process DIANA-TarBase v9.0 Targets & SFARI ASD Risk Genes ---


def process_target_genes(
    raw_mature_set: Set[str],
    mature_precursor_map: Dict[str, Set[str]],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any], Dict[str, int]]:
    """
    Process DIANA-TarBase v9 and miRTarBase 10.0 targets, cross-referencing with SFARI.

    Includes strong evidence interactions (Reporter assay, Western blot, qPCR,
    etc.), all experimental assays for SFARI ASD risk genes (CLIP-seq, CLASH,
    RIP-seq, RNA-seq), and multi-assay targets with evidence tier categorization.
    Annotates each interaction with its database source
    (TarBase, miRTarBase, or Consensus).

    Parameters
    ----------
    raw_mature_set : Set[str]
        Set of raw mature miRNA IDs from miR4ASD.
    mature_precursor_map : Dict[str, Set[str]]
        Mapping from mature miRNA ID to set of precursor miRNA IDs.

    Returns
    -------
    Tuple[List[Dict[str, Any]], Dict[str, Any], Dict[str, int]]
        (target_records, target_stats, per_mirna_target_counts)
    """
    tarbase_path = os.path.join("raw_data", "Homo_sapiens_TarBase-v9.tsv.gz")
    mirtarbase_path = os.path.join("raw_data", "hsa_MTI.csv")
    sfari_path = os.path.join("raw_data", "sfari_genes.csv")

    if not os.path.exists(sfari_path):
        print(f"Warning: SFARI file ({sfari_path}) not found.")
        return [], {}, {}

    if not os.path.exists(tarbase_path) and not os.path.exists(mirtarbase_path):
        print(
            f"Warning: Neither TarBase ({tarbase_path}) "
            f"nor miRTarBase ({mirtarbase_path}) found."
        )
        return [], {}, {}

    # 1. Load SFARI Genes
    df_sfari = pd.read_csv(sfari_path)
    sfari_dict = {}
    for _, row in df_sfari.iterrows():
        sym = str(row["gene-symbol"]).strip().upper()
        score_raw = (
            str(row["gene-score"]).strip() if pd.notna(row["gene-score"]) else ""
        )
        syndromic_raw = (
            int(row["syndromic"])
            if pd.notna(row["syndromic"]) and str(row["syndromic"]).isdigit()
            else 0
        )

        score_label = ""
        if score_raw in ["1", "1.0"]:
            score_label = "Category 1"
        elif score_raw in ["2", "2.0"]:
            score_label = "Category 2"
        elif score_raw in ["3", "3.0"]:
            score_label = "Category 3"

        if syndromic_raw == 1:
            score_label = (
                f"{score_label}, Syndromic".strip(", ") if score_label else "Syndromic"
            )

        gene_full_desc = (
            str(row["gene-name"]).strip() if pd.notna(row["gene-name"]) else ""
        )
        sfari_dict[sym] = {
            "gene_name": gene_full_desc,
            "sfari_score": score_label,
            "is_sfari": True,
        }

    # 2. Experimental Method Tiers
    strong_methods = {
        "Luciferase Reporter Assay",
        "Western Blot",
        "qPCR",
        "Northern Blot",
        "Biotin-qPCR",
        "ELISA",
        "Immunofluorescence",
        "Immunohistochemistry",
        "In Situ Hybridization",
        "Flow Cytometry",
        "Genetic Testing",
        "Luciferase reporter assay",
        "Western blot",
        "Western blotting",
        "qRT-PCR",
        "Northern blot",
    }
    clip_methods = {
        "HITS-CLIP",
        "PAR-CLIP",
        "CLASH",
        "qCLASH",
        "RIP-Seq",
        "AGO-IP",
        "IMPACT-Seq",
        "3LIFE",
        "TRAP",
        "CLIP-seq",
        "eCLIP",
    }

    # Build lookup set for matching miRNAs (both exact and case-normalized)
    mirna_lookup = {m.strip(): m.strip() for m in raw_mature_set if m.strip()}
    mirna_lower_lookup = {
        m.strip().lower(): m.strip() for m in raw_mature_set if m.strip()
    }

    interaction_map = {}

    # Helper to retrieve canonical miRNA ID
    def get_canonical_mirna(raw_name):
        clean_name = str(raw_name).strip()
        if not clean_name:
            return None
        canon = mirna_lookup.get(clean_name) or mirna_lower_lookup.get(
            clean_name.lower()
        )
        if canon:
            return canon
        lower = clean_name.lower()
        if lower.startswith("hsa-"):
            return mirna_lower_lookup.get(lower[4:])
        return mirna_lower_lookup.get(f"hsa-{lower}")

    # 3. Process DIANA-TarBase v9.0 (if present)
    if os.path.exists(tarbase_path):
        print(f"Processing DIANA-TarBase v9: {tarbase_path}")
        with gzip.open(tarbase_path, "rt", encoding="utf-8", errors="ignore") as f:
            for chunk in pd.read_csv(
                f,
                sep="\t",
                chunksize=250000,
                low_memory=False,
                usecols=[
                    "mirna_name",
                    "mirna_id",
                    "gene_name",
                    "gene_id",
                    "experimental_method",
                    "regulation",
                    "tissue",
                    "cell_line",
                    "article_pubmed_id",
                ],
            ):
                for _, row in chunk.iterrows():
                    canonical_mir = get_canonical_mirna(row["mirna_name"])
                    if not canonical_mir:
                        continue

                    gene_sym = str(row["gene_name"]).strip()
                    if not gene_sym or gene_sym == "nan":
                        continue

                    pair_key = (canonical_mir, gene_sym)
                    if pair_key not in interaction_map:
                        interaction_map[pair_key] = {
                            "canonical_mir": canonical_mir,
                            "gene_symbol": gene_sym,
                            "gene_id": (
                                str(row["gene_id"]).strip()
                                if pd.notna(row["gene_id"])
                                else ""
                            ),
                            "sources": set(),
                            "methods": set(),
                            "regulations": set(),
                            "tissues": set(),
                            "cell_lines": set(),
                            "pmids": set(),
                            "has_strong": False,
                            "has_clip": False,
                            "is_sfari": gene_sym.upper() in sfari_dict,
                        }

                    entry = interaction_map[pair_key]
                    entry["sources"].add("TarBase")
                    m = (
                        str(row["experimental_method"]).strip()
                        if pd.notna(row["experimental_method"])
                        else ""
                    )
                    if m:
                        entry["methods"].add(m)
                        if m in strong_methods:
                            entry["has_strong"] = True
                        if m in clip_methods or "CLIP" in m or "CLASH" in m:
                            entry["has_clip"] = True

                    if (
                        pd.notna(row["regulation"])
                        and str(row["regulation"]).strip() != "NA"
                    ):
                        reg = str(row["regulation"]).strip()
                        if reg.lower() == "negative":
                            entry["regulations"].add("Negative (Downregulation)")
                        elif reg.lower() == "positive":
                            entry["regulations"].add("Positive (Upregulation)")
                        else:
                            entry["regulations"].add(reg)

                    if pd.notna(row["tissue"]) and str(row["tissue"]).strip() not in [
                        "NA",
                        "nan",
                        "",
                    ]:
                        entry["tissues"].add(str(row["tissue"]).strip())

                    if pd.notna(row["article_pubmed_id"]):
                        pmid_val = parse_pmid(row["article_pubmed_id"])
                        if pmid_val:
                            entry["pmids"].add(pmid_val)

    # 4. Process miRTarBase 10.0 (if present)
    if os.path.exists(mirtarbase_path):
        print(f"Processing miRTarBase 10.0: {mirtarbase_path}")
        with open(mirtarbase_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                st = (row.get("Support Type") or "").strip()
                if "Non-Functional" in st:
                    continue

                canonical_mir = get_canonical_mirna(row.get("miRNA"))
                if not canonical_mir:
                    continue

                gene_sym = (row.get("Target Gene") or "").strip()
                if not gene_sym or gene_sym == "nan":
                    continue

                is_sfari = gene_sym.upper() in sfari_dict
                is_strong = st == "Functional MTI"

                # Biological inclusion criterion: Strong evidence OR SFARI ASD risk gene
                if not is_strong and not is_sfari:
                    continue

                pair_key = (canonical_mir, gene_sym)
                if pair_key not in interaction_map:
                    interaction_map[pair_key] = {
                        "canonical_mir": canonical_mir,
                        "gene_symbol": gene_sym,
                        "gene_id": (
                            str(row.get("Target Gene (Entrez ID)", "")).strip()
                        ),
                        "sources": set(),
                        "methods": set(),
                        "regulations": set(),
                        "tissues": set(),
                        "cell_lines": set(),
                        "pmids": set(),
                        "has_strong": False,
                        "has_clip": False,
                        "is_sfari": is_sfari,
                    }

                entry = interaction_map[pair_key]
                entry["sources"].add("miRTarBase")
                if is_strong:
                    entry["has_strong"] = True

                experiments_raw = row.get("Experiments") or ""
                for exp in experiments_raw.split("//"):
                    exp_clean = exp.strip()
                    if exp_clean:
                        entry["methods"].add(exp_clean)
                        if exp_clean in strong_methods:
                            entry["has_strong"] = True
                        if (
                            exp_clean in clip_methods
                            or "CLIP" in exp_clean.upper()
                            or "CLASH" in exp_clean.upper()
                        ):
                            entry["has_clip"] = True

                pmid_val = parse_pmid(row.get("References (PMID)"))
                if pmid_val:
                    entry["pmids"].add(pmid_val)

    # 5. Structure Target Records with Provenance Annotation
    target_records = []
    unique_target_genes = set()
    unique_sfari_genes = set()
    per_mirna_target_counts = {}

    for (canonical_mir, gene_sym), data in interaction_map.items():
        # Include all Strong Evidence + all SFARI Target Genes across all assays
        if not data["has_strong"] and not data["is_sfari"]:
            continue

        gene_upper = gene_sym.upper()
        unique_target_genes.add(gene_upper)

        sfari_info = sfari_dict.get(gene_upper, None)
        is_sfari = sfari_info is not None
        sfari_score = sfari_info["sfari_score"] if sfari_info else ""
        gene_full_name = sfari_info["gene_name"] if sfari_info else ""

        if is_sfari:
            unique_sfari_genes.add(gene_upper)

        # Track per-miRNA counts
        if canonical_mir not in per_mirna_target_counts:
            per_mirna_target_counts[canonical_mir] = {"total": 0, "sfari": 0}
        per_mirna_target_counts[canonical_mir]["total"] += 1
        if is_sfari:
            per_mirna_target_counts[canonical_mir]["sfari"] += 1

        # Evidence tier
        if data["has_strong"]:
            evidence_level = "Strong Evidence"
        elif data["has_clip"]:
            evidence_level = "Direct Binding (CLIP/CLASH)"
        else:
            evidence_level = "High-Throughput Expression"

        # Database Source Provenance Annotation
        sources = data.get("sources", set())
        if "TarBase" in sources and "miRTarBase" in sources:
            db_source = "TarBase & miRTarBase (Consensus)"
        elif "miRTarBase" in sources:
            db_source = "miRTarBase 10.0"
        else:
            db_source = "DIANA-TarBase v9.0"

        # Precursor miRNAs
        precursors = mature_precursor_map.get(canonical_mir, set())
        raw_precursor = "; ".join(sorted(precursors)) if precursors else ""

        # Format PMIDs
        pmids_sorted = sorted(list(data["pmids"]))
        pmids_str = "; ".join(pmids_sorted) if pmids_sorted else ""

        methods_str = (
            "; ".join(sorted(list(data["methods"]))) if data["methods"] else "—"
        )
        regs_str = (
            "; ".join(sorted(list(data["regulations"]))) if data["regulations"] else "—"
        )
        tissue_str = (
            "; ".join(sorted(list(data["tissues"]))) if data["tissues"] else "—"
        )

        target_records.append(
            {
                "precursor_mirna": raw_precursor,
                "mature_mirna": canonical_mir,
                "gene_symbol": gene_sym,
                "gene_name": gene_full_name if gene_full_name else gene_sym,
                "is_sfari": is_sfari,
                "sfari_score": sfari_score if sfari_score else "Non-SFARI",
                "evidence_level": evidence_level,
                "database_source": db_source,
                "experimental_methods": methods_str,
                "regulation": regs_str,
                "tissue": tissue_str,
                "pmids": pmids_str,
            }
        )

    # Sort target records: SFARI rank first, then Strong evidence rank, then Gene Symbol
    def sort_key(rec):
        sfari_rank = 0 if rec["is_sfari"] else 1
        strong_rank = 0 if "Strong" in rec["evidence_level"] else 1
        return (sfari_rank, strong_rank, rec["gene_symbol"], rec["mature_mirna"])

    target_records.sort(key=sort_key)

    target_stats = {
        "total_target_genes": len(unique_target_genes),
        "total_sfari_target_genes": len(unique_sfari_genes),
        "total_target_interactions": len(target_records),
        "consensus_interactions": sum(
            1
            for r in target_records
            if r["database_source"] == "TarBase & miRTarBase (Consensus)"
        ),
        "tarbase_interactions": sum(
            1
            for r in target_records
            if "DIANA" in r["database_source"] or "Consensus" in r["database_source"]
        ),
        "mirtarbase_interactions": sum(
            1 for r in target_records if "miRTarBase" in r["database_source"]
        ),
    }

    return target_records, target_stats, per_mirna_target_counts


# --- Calculate and Save Statistics ---


def calculate_and_save_statistics(
    df_expr: pd.DataFrame,
    total_studies_count: int,
    total_genes_count: int,
    total_mature_count: int,
    target_stats: Dict[str, Any],
    output_file: str = "statistics.json",
) -> None:
    """
    Calculate summary statistics and save as JSON.

    Parameters
    ----------
    df_expr : pandas.DataFrame
        The processed expression studies.
    total_studies_count : int
        Total unique studies.
    total_genes_count : int
        Total unique miRNA IDs.
    total_mature_count : int
        Total unique miRNA mature IDs.
    target_stats : dict
        Target gene interaction statistics.
    output_file : str
        Destination path for statistics.json.
    """
    # Expression alteration counts (sum of upregulated/downregulated counts)
    alteration_counts = {
        "upregulated": int(df_expr["upregulation_studies"].sum()),
        "downregulated": int(df_expr["downregulation_studies"].sum()),
    }

    # Standardize, split, and count individual tissues from expression studies
    tissue_counts = {}
    for tissue_str in df_expr["tissue"].dropna():
        for part in str(tissue_str).split(";"):
            part_clean = part.strip()
            if not part_clean:
                continue

            # Standard title-casing for consistent display
            part_clean = (
                part_clean[0].upper() + part_clean[1:]
                if len(part_clean) > 0
                else part_clean
            )

            tissue_counts[part_clean] = tissue_counts.get(part_clean, 0) + 1

    stats = {
        "total_studies": total_studies_count,
        "total_mirna_genes": total_genes_count,
        "total_mirna_mature": total_mature_count,
        "alteration_counts": alteration_counts,
        "tissue_counts": tissue_counts,
        "target_stats": target_stats,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)


def main(
    excel_path: str = "Tabelas_miR4ASD.xlsx",
    gff_path: str = "hsa.gff3",
    output_dir: str = ".",
) -> None:
    """
    Execute the full miR4ASD ETL and database generation pipeline.

    Parameters
    ----------
    excel_path : str
        Path to the primary Excel spreadsheet.
    gff_path : str
        Path to miRBase GFF3 human annotations.
    output_dir : str
        Destination directory for generated JSON feeds.
    """
    # Ensure GFF maps are cached
    get_gff_maps(gff_path)

    if os.path.exists(excel_path):
        # Read the Excel file
        xls = pd.ExcelFile(excel_path)

        # Read the sheets into dataframes
        df_expression = pd.read_excel(xls, "miRNA_expression_studies")
        df_other = pd.read_excel(xls, "miRNA_other_studies")
        df_details = pd.read_excel(xls, "miRNA_study_details")

        # Clean column names
        df_expression = clean_col_names(df_expression)
        df_other = clean_col_names(df_other)
        df_details = clean_col_names(df_details)

        # Harmonize column names for df_details
        details_rename_map = {
            "Paper": "Study",
            "Reference (DOI)": "DOI",
            "Study methods": "Title",
        }
        df_details = df_details.rename(columns=details_rename_map)
        df_details["Study"] = df_details["Study"].astype(str).str.strip()

        study_details_records = df_details.to_dict(orient="records")
        study_details_map = {study["Study"]: study for study in study_details_records}

        # Standardize delimiters and resolve study details
        df_expression = standardize_delimiters(df_expression, ["Study", "Tissue"])
        df_expression["StudyDetails"] = df_expression["Study"].apply(
            lambda s: resolve_study_details(s, study_details_map)
        )
        df_expression = df_expression.drop(columns=["Study", "Study Type"])
        df_expression = df_expression.rename(
            columns={
                "miRNA ID": "precursor_mirna",
                "miRNA mature ID": "mature_mirna",
                "Expression Change": "expression_change",
                "Study description": "study_description",
                "Tissue": "tissue",
                "Expression": "expression",
                "Upregulation studies": "upregulation_studies",
                "Downregulation studies": "downregulation_studies",
            }
        )

        df_other = standardize_delimiters(df_other, ["Study", "Study description"])
        df_other["StudyDetails"] = df_other["Study"].apply(
            lambda s: resolve_study_details(s, study_details_map)
        )
        df_other = df_other.drop(columns=["Study", "Study Type"])
        df_other = df_other.rename(
            columns={
                "miRNA ID": "precursor_mirna",
                "miRNA mature ID": "mature_mirna",
                "Alteration": "alteration",
                "Study description": "study_description",
            }
        )

        # Build mature -> precursors mapping
        mature_to_precursors = {}
        for _, row in (
            pd.concat(
                [
                    df_expression[["mature_mirna", "precursor_mirna"]],
                    df_other[["mature_mirna", "precursor_mirna"]],
                ]
            )
            .dropna()
            .iterrows()
        ):
            mat = str(row["mature_mirna"]).strip()
            hair = str(row["precursor_mirna"]).strip()
            if mat:
                if mat not in mature_to_precursors:
                    mature_to_precursors[mat] = set()
                if hair:
                    mature_to_precursors[mat].add(hair)

        raw_mirna_ids = (
            pd.concat([df_expression["precursor_mirna"], df_other["precursor_mirna"]])
            .dropna()
            .astype(str)
            .str.strip()
        )
        total_mirna_genes = int(raw_mirna_ids.nunique())

        raw_mature_ids = (
            pd.concat([df_expression["mature_mirna"], df_other["mature_mirna"]])
            .dropna()
            .astype(str)
            .str.strip()
        )
        total_mirna_mature = int(raw_mature_ids.nunique())
        unique_total_studies = int(df_details["Study"].nunique())

        # Apply link generation
        df_expression["precursor_mirna"] = df_expression["precursor_mirna"].apply(
            create_mirbase_hairpin_link
        )
        df_other["precursor_mirna"] = df_other["precursor_mirna"].apply(
            create_mirbase_hairpin_link
        )
        df_expression["mature_mirna"] = df_expression["mature_mirna"].apply(
            create_mirbase_mature_link
        )
        df_other["mature_mirna"] = df_other["mature_mirna"].apply(
            create_mirbase_mature_link
        )
    else:
        print(
            f"Notice: {excel_path} not found. "
            "Using existing JSON feeds for miRNA mappings."
        )
        with open("expression_studies.json", "r", encoding="utf-8") as f:
            expr_data = json.load(f)
        with open("other_studies.json", "r", encoding="utf-8") as f:
            other_data = json.load(f)
        with open("study_details.json", "r", encoding="utf-8") as f:
            study_details_records = json.load(f)

        df_expression = pd.DataFrame(expr_data)
        df_other = pd.DataFrame(other_data)
        df_details = pd.DataFrame(study_details_records)

        def clean_raw_mir(val):
            if not val or pd.isna(val):
                return ""
            s = str(val).strip()
            if "<" in s:
                return s.split(">")[-2].split("<")[0].strip()
            return s

        mature_to_precursors = {}
        raw_matures = []
        raw_precursors = []

        for r in expr_data + other_data:
            mat = clean_raw_mir(r.get("mature_mirna"))
            hair = clean_raw_mir(r.get("precursor_mirna"))
            if mat:
                raw_matures.append(mat)
                if mat not in mature_to_precursors:
                    mature_to_precursors[mat] = set()
                if hair:
                    mature_to_precursors[mat].add(hair)
            if hair:
                raw_precursors.append(hair)

        raw_mature_ids = pd.Series(raw_matures)
        total_mirna_genes = len(set(raw_precursors))
        total_mirna_mature = len(set(raw_matures))
        unique_total_studies = len(study_details_records)

    # Process target genes
    target_records, target_stats, per_mirna_counts = process_target_genes(
        raw_mature_ids, mature_to_precursors
    )

    # Save target_genes.json
    target_genes_path = os.path.join(output_dir, "target_genes.json")
    with open(target_genes_path, "w", encoding="utf-8") as f:
        json.dump(target_records, f, separators=(",", ":"), ensure_ascii=False)

    # Save expression, other, and details
    df_expression.to_json(
        os.path.join(output_dir, "expression_studies.json"),
        orient="records",
        default_handler=str,
    )
    df_other.to_json(
        os.path.join(output_dir, "other_studies.json"),
        orient="records",
        default_handler=str,
    )
    df_details.to_json(
        os.path.join(output_dir, "study_details.json"),
        orient="records",
        default_handler=str,
    )

    # Save statistics
    calculate_and_save_statistics(
        df_expression,
        unique_total_studies,
        total_mirna_genes,
        total_mirna_mature,
        target_stats,
        output_file=os.path.join(output_dir, "statistics.json"),
    )

    print("Data processing complete. JSON files created.")
    print(f"Expression Studies count: {len(df_expression)}")
    print(f"Other Studies count: {len(df_other)}")
    print(f"Target Interactions count: {len(target_records)}")
    print(f"Target Statistics: {target_stats}")


if __name__ == "__main__":
    main()
