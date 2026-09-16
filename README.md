# *miR4ASD*: A Database of microRNAs Associated with Autism Spectrum Disorder

[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Package Manager: uv](https://img.shields.io/badge/Package%20Manager-uv-blueviolet.svg)](https://docs.astral.sh/uv/)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

**miR4ASD** is an open-access, literature-curated database and web interface that catalogs human microRNAs (miRNAs) experimentally associated with Autism Spectrum Disorder (ASD). It compiles findings from case-control expression studies, genetic variant analyses (CNVs, SNVs, SNPs), and standardized miRBase annotations.

🌐 **Live Application:** [https://miR4ASD.github.io/miR4ASD](https://miR4ASD.github.io/miR4ASD)  
📁 **Repository:** [https://github.com/miR4ASD/miR4ASD](https://github.com/miR4ASD/miR4ASD)

---

## Key Features

* **Interactive Triple Tables:** Fast, client-side exploration using DataTables 2.0 with pagination, column sorting, and CSV export.
  * **Expression Studies Tab:** Precursor/mature miRNA, observed expression change, sample type (`Sample Type`), multi-study consistency synthesis (`Overall evidence`), cross-study genetic/bioinformatic support, and publication tallies (`# up`, `# down`, `Total studies`).
  * **Genetic & Other Studies Tab:** Precursor/mature miRNA, genomic variant classifications (`CNVs`, `SNVs`, `SNPs`), cross-referencing to expression studies, and study methodology.
  * **Validated Target Genes Tab:** Comprehensive catalog of **17,150 experimentally supported target interactions** across **2,995 target genes** (including **843 SFARI ASD-risk genes**), sourced exclusively from **miRTarBase 10.0** with **functional experimental validation** (Reporter assays, Western blot, qPCR, CLIP-Seq) and cross-referenced with **SFARI Gene** ASD-risk susceptibility scores. *(Note: DIANA-TarBase is no longer used in this version).*
* **Sole-Source miRTarBase 10.0 Target Provenance:**
  * **Gold-Standard Validation:** All target interactions derive directly from **miRTarBase 10.0**, the premier curated repository of experimentally validated miRNA-target interactions.
  * **Explicit Provenance Badges:** Prominent `miRTarBase 10.0` indicators across the Target Genes tab and Functional Enrichment workflows.
  * **Target Interaction Attributes:** Catalogs precursor/mature miRNA identifiers, official HGNC target gene symbols, gene descriptions, SFARI autism susceptibility scores, support classifications (`Functional MTI` vs. `Weak Support`), validation assay techniques (reporter assays, Western blot, qPCR, CLIP-Seq), and clickable PubMed PMIDs.
* **Functional Enrichment Analysis (g:Profiler):** Seamless downstream systems biology workflow connecting filtered miRNAs to pathway overrepresentation analysis.
  * **Strict miRNA-First Architecture:** Enrichment target resolution is derived exclusively from user-selected miRNAs.
  * **Target Gene Customization:** Candidate gene set automatically resolves validated targets for selected miRNAs, with real-time gene set stats, SFARI breakdowns, and full support to copy, edit, or supply custom gene symbols.
  * **Multi-Ontology Analysis:** Query Gene Ontology (Biological Process, Molecular Function, Cellular Component), KEGG Pathways, Reactome, WikiPathways, and Human Phenotype Ontology (`HP`).
  * **Interactive Visualizations:** Chart.js horizontal bar charts ranked by $-\log_{10}(P_{\text{adj}})$, metric summary ribbons, and dedicated interactive DataTables with intersecting gene badges and direct GeneCards links.
  * **Export & Web Portal:** One-click CSV export and direct submission to the official [g:Profiler web portal](https://biit.cs.ut.ee/gprofiler/gost).
* **Multi-Tiered Experimental Evidence & SFARI Integration:**
  * **Evidence Tiers:** Classified into **Strong Evidence** (Luciferase Reporter Assays, Western Blot, qPCR, Northern Blot, ELISA), **Direct Physical Binding** (HITS-CLIP, PAR-CLIP, CLASH, qCLASH, RIP-Seq, AGO-IP), and **High-Throughput Expression** (RNA-Seq, Microarrays).
  * **SFARI ASD Susceptibility Categories:** Visual badges for Category 1 (High Confidence), Category 2 (Strong Candidate), Category 3 (Suggestive), and Syndromic genes.
  * **Direct Resource Links:** Clickable links to [GeneCards](https://www.genecards.org/) for target genes and [PubMed](https://pubmed.ncbi.nlm.nih.gov/) for primary literature references.
* **Unified Advanced Filter Drawer:**
  * **Shared Filters:** Filter all tables simultaneously by Precursor Hairpin ID or Mature miRNA ID.
  * **Expression Filters:** Targeted filtering by Sample Type (multi-select checklist), Expression Change direction (Upregulated/Downregulated), Overall Evidence consistency, minimum study thresholds (`Min # up`, `Min # down`, `Min total`), and study-level Methodology & Diagnostic Tools.
  * **Genetic Filters:** Filter by Variant Type (`CNV`, `SNV`, `SNP`), Study Description, and study-level Methodology & Diagnostic Tools.
  * **Target Genes Filters:** Filter by Target Gene Symbol, SFARI ASD Risk Category (multi-select OR), Support Type (`Functional MTI`, `Weak Support`), and Experimental Technique.
  * **Subtable Methodology & Diagnostic Reactivity:** Main table rows are reactively filtered based on matching nested study records in expandable child rows.
  * **Cross-Tab Filter Memory & Single-Click Reset:** Filters remain active during tab navigation and can be cleared instantly.
* **Master-Detail Expandable Rows:** Click the `+` icon on any entry to reveal nested study metadata including DOI hyperlinks, multi-cohort sample sizes (ASD vs. control counts formatted as distinct pill badges for semicolon-separated cohorts), sample types, sample subtypes, diagnostic tools, and origin countries.
* **Help Tab & Reference Specifications:**
  * **Interactive Data Dictionary:** Full in-app specification accordion detailing definitions, purpose, and categorical values across all tables.
  * **Molecular Methodologies Table:** Standardized definitions and study types for assays (RT-qPCR, Small RNA-seq, WES, WGS, SNP array, etc.).
  * **Clinical Diagnostic Tools Table:** Detailed catalog of clinical criteria and rating instruments (DSM-5, ADOS, ADI-R, CARS, SRS, etc.).
* **Automatic miRBase Hyperlinking:** Precursor hairpins and mature miRNAs automatically resolve to their respective [miRBase](https://www.mirbase.org/) entry pages.
* **High-Resolution Visualizations:** Interactive About section containing curation workflows, distribution charts, and image lightbox zoom.

---

## Project Architecture

```
mir4ASD/
├── process_data.py                      # Python ETL pipeline (Excel + GFF3 + miRTarBase 10.0 + SFARI -> JSON feeds)
├── index.html                           # Single-page frontend application
├── Tabelas_miR4ASD(site)_15.09.2026.xlsx# Latest curated primary dataset
├── Tables_for_help_tab.xlsx             # Standardized methodologies & diagnostic tools definitions
├── hsa.gff3                             # miRBase v22.1 human miRNA annotations
├── raw_data/                            # Raw reference datasets
│   ├── hsa_MTI.csv                      # miRTarBase 10.0 experimentally validated targets
│   ├── sfari_genes.csv                  # SFARI Gene autism risk scores
│   └── Tabelas_miR4ASD(site)_15.09.2026.xlsx # Literature-curated primary tables
├── expression_studies.json              # Processed JSON feed: Expression studies
├── other_studies.json                   # Processed JSON feed: Genetic & other studies
├── target_genes.json                    # Processed JSON feed: Experimental target interactions
├── study_details.json                   # Processed JSON feed: Study metadata & DOIs
├── help_methods.json                    # Processed JSON feed: Molecular methodologies
├── help_diagnostic_tools.json           # Processed JSON feed: Clinical diagnostic tools
├── statistics.json                      # Processed JSON feed: Summary statistics
├── pyproject.toml                       # Project configuration (uv, ruff, pytest)
├── Makefile                             # Automation workflows (build, test, lint, serve)
├── images/                              # Charts, figures, and workflow diagrams
├── tests/                               # Automated unit and Playwright E2E tests
└── docs/                                # Technical documentation
    └── data_dictionary.md               # Complete data dictionary & column reference
```

📖 **Detailed Data Dictionary:** See [`docs/data_dictionary.md`](docs/data_dictionary.md) for full descriptions of all table headers, data types, sources of truth, and categorical enumerations.

---

## Quick Start & Usage

### Prerequisites
* Python 3.10+
* [`uv`](https://docs.astral.sh/uv/) (recommended) or standard `pip`

### 1. Environment Setup

Using `uv` (recommended):
```bash
# Sync dependencies from pyproject.toml
uv sync
```

Alternatively with standard `pip`:
```bash
pip install pandas openpyxl pytest ruff
```

---

### 2. Processing Data (ETL Pipeline)

To re-process the raw Excel dataset ([`raw_data/Tabelas_miR4ASD(site)_15.09.2026.xlsx`](raw_data/Tabelas_miR4ASD(site)_15.09.2026.xlsx)) and regenerate all JSON feeds:

```bash
# Using Makefile
make data

# Or directly with Python
python3 process_data.py
# Or with uv
uv run python process_data.py
```

This updates:
* `expression_studies.json`
* `other_studies.json`
* `target_genes.json`
* `study_details.json`
* `help_methods.json`
* `help_diagnostic_tools.json`
* `statistics.json`

---

### 3. Running the Local Web Server

Browsers block local asynchronous `fetch()` requests when opening `index.html` via `file:///`. Use a local web server to preview:

```bash
# Using Makefile
make serve

# Or directly with Python
python3 -m http.server 8000
```

Then navigate to: **[http://localhost:8000](http://localhost:8000)** in your browser.

---

### 4. Running Tests, Linting & Formatting

```bash
# Run pytest test suite
make test
# (or: uv run pytest)

# Run ruff linter
make lint
# (or: uv run ruff check .)

# Format code with ruff
make format
# (or: uv run ruff format .)
```

---

## Makefile Reference

| Target | Description |
| :--- | :--- |
| `make data` | Executes `process_data.py` to regenerate JSON feeds. |
| `make serve` | Launches a local HTTP development server at `http://localhost:8000`. |
| `make test` | Runs the automated `pytest` suite in `tests/`. |
| `make lint` | Runs `ruff` checks across all Python files. |
| `make format` | Formats all Python code using `ruff`. |
| `make clean` | Cleans temporary cache and build artifacts. |
| `make help` | Displays help information for all targets. |

---

## License & Citation

* **Data & Application License:** [Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).
* **Citation:** If you use miR4ASD in your research, please cite the database repository and the associated publication.
