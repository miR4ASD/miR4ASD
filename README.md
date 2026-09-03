# *miR4ASD*: A Database of microRNAs Associated with Autism Spectrum Disorder

[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Package Manager: uv](https://img.shields.io/badge/Package%20Manager-uv-blueviolet.svg)](https://docs.astral.sh/uv/)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

**miR4ASD** is an open-access, literature-curated database and web interface that catalogs human microRNAs (miRNAs) experimentally associated with Autism Spectrum Disorder (ASD). It compiles findings from case-control expression studies, genetic variant analyses (CNVs, SNVs), and standardized miRBase annotations.

🌐 **Live Application:** [https://miR4ASD.github.io/miR4ASD](https://miR4ASD.github.io/miR4ASD)  
📁 **Repository:** [https://github.com/miR4ASD/miR4ASD](https://github.com/miR4ASD/miR4ASD)

---

## Key Features

* **Interactive Triple Tables:** Fast, client-side exploration using DataTables 2.0 with pagination, column sorting, and CSV export.
  * **Expression Studies Tab:** Precursor/mature miRNA, observed expression change, tissue localization, and study consistency evidence.
  * **Genetic & Other Studies Tab:** Precursor/mature miRNA, variant alteration types (CNVs, SNVs), and descriptive methodology.
  * **Validated Target Genes Tab:** Comprehensive catalog of **78,153 experimental target interactions** across **3,281 target genes** (including **901 SFARI ASD-risk genes**), integrating **miRTarBase 10.0** and **DIANA-TarBase v9.0** with **7,492 cross-database consensus interactions** and **miRTarBase 10.0 as the default interactive view**.
* **Dual-Database Provenance & Interactive Switcher:**
  * **Database Toggle Toolbar:** Instantly toggle between **miRTarBase 10.0 (Default)**, **Consensus (Both DBs)**, **DIANA-TarBase v9.0**, and **All Sources (Union)**.
  * **Provenance Badges:** Color-coded badges for *miRTarBase 10.0*, *DIANA-TarBase v9.0*, and gold-accented *Consensus (Both)*.
* **Functional Enrichment Analysis (g:Profiler):** Seamless downstream systems biology workflow connecting filtered miRNAs to pathway overrepresentation analysis.
  * **Strict miRNA-First Architecture:** Enrichment target resolution is derived exclusively from user-selected miRNAs.
  * **Dual Database & Target Scope Controls:** Non-destructively filter target cohorts by database source (miRTarBase default, Consensus, TarBase, All) and biological criteria (*All Targets*, *Strong Evidence*, *SFARI Risk*, *SFARI Cat 1*, *Brain Targets*, *Upregulated*, *Downregulated*).
  * **Multi-Ontology Analysis:** Query Gene Ontology (Biological Process, Molecular Function, Cellular Component), KEGG Pathways, Reactome, WikiPathways, and Human Phenotype Ontology (`HP`).
  * **Interactive Visualizations:** Chart.js horizontal bar charts ranked by $-\log_{10}(P_{\text{adj}})$, metric summary ribbons, and dedicated interactive DataTables with intersecting gene badges and direct GeneCards links.
  * **Export & Web Portal:** One-click CSV export and direct submission to the official [g:Profiler web portal](https://biit.cs.ut.ee/gprofiler/gost).
* **Multi-Tiered Experimental Evidence & SFARI Integration:**
  * **Evidence Tiers:** Classified into **Strong Evidence** (Luciferase Reporter Assays, Western Blot, qPCR, Northern Blot, ELISA), **Direct Physical Binding** (HITS-CLIP, PAR-CLIP, CLASH, qCLASH, RIP-Seq, AGO-IP), and **High-Throughput Expression** (RNA-Seq, Microarrays).
  * **SFARI ASD Susceptibility Categories:** Visual badges for Category 1 (High Confidence), Category 2 (Strong Candidate), Category 3 (Suggestive), and Syndromic genes.
  * **Direct Resource Links:** Clickable links to [GeneCards](https://www.genecards.org/) for target genes and [PubMed](https://pubmed.ncbi.nlm.nih.gov/) for primary literature references.
* **Unified Advanced Filter Drawer:**
  * **Shared Filters:** Filter all tables simultaneously by Hairpin ID or Mature ID.
  * **Target Genes Filters:** Filter by Target Database Source, Target Gene Symbol, SFARI Category, Evidence Level, Experimental Technique, Regulation (Down/Up), and Tissue/Cell Source.
  * **Expression Filters:** Targeted filtering by expression change direction (Up/Down), overall evidence type, and tissue type checklists.
  * **Genetic Filters:** Filter by variant alteration type and search study descriptions.
  * **Cross-Tab Filter Memory:** Filters remain active when navigating between tabs.
  * **Single-Click Reset:** Quickly reset all filters across all tables.
* **Master-Detail Expandable Rows:** Click the `+` icon on any entry to reveal nested study metadata including DOI hyperlinks, sample sizes (ASD vs. control), tissue subtypes, and origin countries.
* **Automatic miRBase Hyperlinking:** Precursor hairpins and mature miRNAs automatically resolve to their respective [miRBase](https://www.mirbase.org/) entry pages.
* **High-Resolution Visualizations:** Interactive About section containing curation workflows, distribution charts, and image lightbox zoom.

---

## Project Architecture

```
mir4ASD/
├── process_data.py            # Python ETL pipeline (Excel + GFF3 + TarBase + SFARI -> JSON feeds)
├── index.html                 # Single-page frontend application
├── Tabelas_miR4ASD.xlsx       # Curated primary dataset
├── hsa.gff3                   # miRBase v22.1 human miRNA annotations
├── raw_data/                  # Raw reference datasets (TarBase v9, SFARI Gene)
├── expression_studies.json    # Processed JSON feed: Expression studies
├── other_studies.json         # Processed JSON feed: Genetic & other studies
├── target_genes.json          # Processed JSON feed: Experimental target interactions
├── study_details.json         # Processed JSON feed: Study metadata & DOIs
├── statistics.json            # Processed JSON feed: Summary statistics
├── pyproject.toml             # Project configuration (uv, ruff, pytest)
├── Makefile                   # Automation workflows (build, test, lint, serve)
├── images/                    # Charts, figures, and workflow diagrams
├── tests/                     # Automated unit and integration tests
├── docs/                      # Manuscript text drafts and database documentation
│   └── data_dictionary.md     # Complete data dictionary & column reference
```

📖 **Detailed Data Dictionary:** See [`docs/data_dictionary.md`](docs/data_dictionary.md) for full descriptions of all table headers, data types, and categorical enumerations.

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

To re-process the raw Excel dataset ([`Tabelas_miR4ASD.xlsx`](file:///home/hugo/Work/Devel/mir4ASD/Tabelas_miR4ASD.xlsx)) and regenerate all JSON feeds:

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
* `study_details.json`
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
