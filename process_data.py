import json

import pandas as pd


def create_gff_maps(gff_file):
    """
    Parse a GFF3 file and create name-to-ID maps for miRNA hairpins and mature miRNAs.

    Parameters
    ----------
    gff_file : str
        The path to the GFF3 file.

    Returns
    -------
    tuple
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


def clean_col_names(df):
    """
    Clean the column names of a DataFrame by stripping whitespace and extra text.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame whose columns should be cleaned.

    Returns
    -------
    pandas.DataFrame
        The DataFrame with cleaned column names.
    """
    cols = df.columns
    new_cols = [col.replace("\n(MIRBASE v22.1)", "").strip() for col in cols]
    df.columns = new_cols
    return df


def normalize_study_name(name):
    """
    Normalize study names to match keys in the study details sheet.

    Parameters
    ----------
    name : str
        The raw study name.

    Returns
    -------
    str
        The normalized study name.
    """
    return str(name).strip()


_GFF_CACHE = None


def get_gff_maps(gff_file="hsa.gff3"):
    """
    Retrieve cached GFF3 maps or load if not initialized.

    Parameters
    ----------
    gff_file : str
        Path to the GFF3 annotation file.

    Returns
    -------
    tuple
        (hairpin_to_id_map, mature_to_id_map, hairpin_lower_map, mature_lower_map)
    """
    global _GFF_CACHE
    if _GFF_CACHE is None:
        hairpin_map, mature_map = create_gff_maps(gff_file)
        hairpin_lower = {k.lower(): v for k, v in hairpin_map.items()}
        mature_lower = {k.lower(): v for k, v in mature_map.items()}
        _GFF_CACHE = (hairpin_map, mature_map, hairpin_lower, mature_lower)
    return _GFF_CACHE


def create_mirbase_hairpin_link(hairpin_name, gff_file="hsa.gff3"):
    """
    Generate HTML anchor for hairpin miRNA pointing to miRBase.

    Parameters
    ----------
    hairpin_name : str
        Name of the precursor miRNA hairpin.
    gff_file : str
        Path to the GFF3 file for ID resolution.

    Returns
    -------
    str
        HTML anchor link or original string.
    """
    if pd.isna(hairpin_name):
        return hairpin_name
    name_str = str(hairpin_name).strip()
    if not name_str:
        return hairpin_name

    hairpin_to_id_map, _, hairpin_lower_map, _ = get_gff_maps(gff_file)

    # 1. Exact match
    if name_str in hairpin_to_id_map:
        mirbase_id = hairpin_to_id_map[name_str]
        return (
            f'<a href="https://www.mirbase.org/hairpin/{mirbase_id}" '
            f'target="_blank">{name_str}</a>'
        )

    # 2. Case-insensitive match
    name_lower = name_str.lower()
    if name_lower in hairpin_lower_map:
        mirbase_id = hairpin_lower_map[name_lower]
        return (
            f'<a href="https://www.mirbase.org/hairpin/{mirbase_id}" '
            f'target="_blank">{name_str}</a>'
        )

    # 3. Try with 'hsa-' prefix if missing
    if not name_lower.startswith("hsa-"):
        prefixed = f"hsa-{name_lower}"
        if prefixed in hairpin_lower_map:
            mirbase_id = hairpin_lower_map[prefixed]
            return (
                f'<a href="https://www.mirbase.org/hairpin/{mirbase_id}" '
                f'target="_blank">{name_str}</a>'
            )

    return name_str


def create_mirbase_mature_link(mature_name, gff_file="hsa.gff3"):
    """
    Generate HTML anchor for mature miRNA pointing to miRBase.

    Parameters
    ----------
    mature_name : str
        Name of the mature miRNA.
    gff_file : str
        Path to the GFF3 file for ID resolution.

    Returns
    -------
    str
        HTML anchor link or original string.
    """
    if pd.isna(mature_name):
        return mature_name
    name_str = str(mature_name).strip()
    if not name_str:
        return mature_name

    _, mature_to_id_map, _, mature_lower_map = get_gff_maps(gff_file)

    # 1. Exact match
    if name_str in mature_to_id_map:
        mirbase_id = mature_to_id_map[name_str]
        return (
            f'<a href="https://www.mirbase.org/mature/{mirbase_id}" '
            f'target="_blank">{name_str}</a>'
        )

    # 2. Case-insensitive match
    name_lower = name_str.lower()
    if name_lower in mature_lower_map:
        mirbase_id = mature_lower_map[name_lower]
        return (
            f'<a href="https://www.mirbase.org/mature/{mirbase_id}" '
            f'target="_blank">{name_str}</a>'
        )

    # 3. Try with 'hsa-' prefix if missing
    if not name_lower.startswith("hsa-"):
        prefixed = f"hsa-{name_lower}"
        if prefixed in mature_lower_map:
            mirbase_id = mature_lower_map[prefixed]
            return (
                f'<a href="https://www.mirbase.org/mature/{mirbase_id}" '
                f'target="_blank">{name_str}</a>'
            )

    return name_str


# --- Process DIANA-TarBase v9.0 Targets & SFARI ASD Risk Genes ---


def process_target_genes(raw_mature_set, mature_precursor_map):
    """
    Process DIANA-TarBase v9 experimental targets and cross-reference with SFARI.

    Includes strong evidence interactions (Reporter assay, Western blot, qPCR,
    etc.), all experimental assays for SFARI ASD risk genes (CLIP-seq, CLASH,
    RIP-seq, RNA-seq), and multi-assay targets with evidence tier categorization.

    Parameters
    ----------
    raw_mature_set : set
        Set of raw mature miRNA IDs from miR4ASD.
    mature_precursor_map : dict
        Mapping from mature miRNA ID to set of precursor miRNA IDs.

    Returns
    -------
    tuple
        (target_records, target_stats, per_mirna_target_counts)
    """
    import gzip
    import os

    tarbase_path = os.path.join("raw_data", "Homo_sapiens_TarBase-v9.tsv.gz")
    sfari_path = os.path.join("raw_data", "sfari_genes.csv")

    if not os.path.exists(tarbase_path) or not os.path.exists(sfari_path):
        print(f"Warning: TarBase ({tarbase_path}) or SFARI ({sfari_path}) not found.")
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
                f"{score_label}, Syndromic".strip(", ")
                if score_label
                else "Syndromic"
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
    }

    # Build lookup set for matching miRNAs (both exact and case-normalized)
    mirna_lookup = {m.strip(): m.strip() for m in raw_mature_set if m.strip()}
    mirna_lower_lookup = {
        m.strip().lower(): m.strip() for m in raw_mature_set if m.strip()
    }

    interaction_map = {}

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
                raw_mir = str(row["mirna_name"]).strip()
                canonical_mir = mirna_lookup.get(raw_mir) or mirna_lower_lookup.get(
                    raw_mir.lower()
                )
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
                m = (
                    str(row["experimental_method"]).strip()
                    if pd.notna(row["experimental_method"])
                    else ""
                )
                if m:
                    entry["methods"].add(m)
                    if m in strong_methods:
                        entry["has_strong"] = True
                    if m in clip_methods:
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

                if (
                    pd.notna(row["tissue"])
                    and str(row["tissue"]).strip() not in ["NA", "nan", ""]
                ):
                    entry["tissues"].add(str(row["tissue"]).strip())

                if pd.notna(row["article_pubmed_id"]):
                    try:
                        pmid_val = str(int(float(row["article_pubmed_id"])))
                        if pmid_val and pmid_val != "0":
                            entry["pmids"].add(pmid_val)
                    except (ValueError, TypeError):
                        pass

    # 3. Structure Target Records
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
            "; ".join(sorted(list(data["regulations"])))
            if data["regulations"]
            else "—"
        )
        tissue_str = (
            "; ".join(sorted(list(data["tissues"]))) if data["tissues"] else "—"
        )

        target_records.append({
            "precursor_mirna": raw_precursor,
            "mature_mirna": canonical_mir,
            "gene_symbol": gene_sym,
            "gene_name": gene_full_name if gene_full_name else gene_sym,
            "is_sfari": is_sfari,
            "sfari_score": sfari_score if sfari_score else "Non-SFARI",
            "evidence_level": evidence_level,
            "experimental_methods": methods_str,
            "regulation": regs_str,
            "tissue": tissue_str,
            "pmids": pmids_str,
        })

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
    }

    return target_records, target_stats, per_mirna_target_counts


# --- Calculate and Save Statistics ---


def calculate_and_save_statistics(
    df_expr,
    total_studies_count,
    total_genes_count,
    total_mature_count,
    target_stats,
    output_file="statistics.json",
):
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
    excel_path="Tabelas_miR4ASD.xlsx",
    gff_path="hsa.gff3",
    output_dir=".",
):
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
    import os

    # Ensure GFF maps are cached
    get_gff_maps(gff_path)

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

    # Standardize delimiters
    df_expression["Study"] = (
        df_expression["Study"].astype(str).str.replace(r"\s*,\s*", "; ", regex=True)
    )
    df_expression["Tissue"] = (
        df_expression["Tissue"].astype(str).str.replace(r"\s*,\s*", "; ", regex=True)
    )

    def get_study_details_for_expression(row):
        study_names = [s.strip() for s in str(row["Study"]).split(";")]
        details_list = []
        for study_name in study_names:
            study_name_norm = normalize_study_name(study_name)
            if study_name_norm in study_details_map:
                details_list.append(study_details_map[study_name_norm])
        return details_list

    df_expression["StudyDetails"] = df_expression.apply(
        get_study_details_for_expression, axis=1
    )

    cols_to_drop = [
        c
        for c in ["Study", "Observations", "Unnamed: 10"]
        if c in df_expression.columns
    ]
    df_expression = df_expression.drop(columns=cols_to_drop)

    df_expression = df_expression.rename(
        columns={
            "Precursor miRNA (hairpin)": "precursor_mirna",
            "Mature miRNA": "mature_mirna",
            "Expression change (ASD vs. controls)": "expression_change",
            "Tissue": "tissue",
            "Overall evidence": "overall_evidence",
            "Number of studies (Upregulated)": "upregulation_studies",
            "Number of studies (Downregulated)": "downregulation_studies",
            "Total studies": "total_studies",
        }
    )

    df_other["Study"] = (
        df_other["Study"].astype(str).str.replace(r"\s*,\s*", "; ", regex=True)
    )
    df_other["Study description"] = (
        df_other["Study description"]
        .astype(str)
        .str.replace(r"\s*,\s*", "; ", regex=True)
    )

    def get_study_details_for_other(row):
        study_names = [s.strip() for s in str(row["Study"]).split(";")]
        details_list = []
        for study_name in study_names:
            study_name_norm = normalize_study_name(study_name)
            if study_name_norm in study_details_map:
                details_list.append(study_details_map[study_name_norm])
        return details_list

    df_other["StudyDetails"] = df_other.apply(get_study_details_for_other, axis=1)
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
        pd.concat([
            df_expression[["mature_mirna", "precursor_mirna"]],
            df_other[["mature_mirna", "precursor_mirna"]],
        ])
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

