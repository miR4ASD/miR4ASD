# miR4ASD Data Dictionary & Column Reference

This document provides a comprehensive specification of all tables, columns, data types, sources, and categorical enumeration values used in the **miR4ASD** database and web application.

---

## 1. Expression Studies Table (`expression_studies.json`)

Primary catalog of human microRNAs evaluated in case-control gene expression profiling studies of Autism Spectrum Disorder (ASD).

| Column Header | JSON Key | Data Type | Description | Allowed / Categorical Values |
| :--- | :--- | :--- | :--- | :--- |
| **Precursor miRNA (hairpin)** | `precursor_mirna` | String (HTML Link) | Official miRBase stem-loop precursor RNA name (links to miRBase). | Standardized to miRBase v22.1 (e.g. `hsa-let-7a-1`, `hsa-mir-146a`). |
| **Mature miRNA** | `mature_mirna` | String (HTML Link) | Fully processed, functional single-stranded mature miRNA identifier. | Standardized to miRBase v22.1 (e.g. `hsa-let-7a-5p`, `hsa-miR-146a-5p`). |
| **Expression change (ASD vs. controls)** | `expression_change` | String | Reported direction of expression alteration in ASD patients compared to neurotypical controls. | <ul><li>`Upregulated`: Statistically significant increased expression in ASD cohort.</li><li>`Downregulated`: Statistically significant decreased expression in ASD cohort.</li></ul> |
| **Tissue** | `tissue` | String (Semicolon-delimited) | Biological specimen or anatomical tissue source analyzed. | `Blood`, `Brain`, `LCLs` (Lymphoblastoid Cell Lines), `Saliva`, `Serum`, `Plasma`, `Post-mortem brain (Cerebellum, Cortex, Temporal cortex, Frontal cortex, Superior temporal gyrus, Vermis)`, `Dental pulp stem cells`, `Umbilical cord blood`, `Olfactory mucosal cells`, `Whole blood`. |
| **Overall evidence** | `overall_evidence` | String | Synthesis of consistency across independent published studies evaluating this miRNA. | <ul><li>`Consistent upregulation`: Two or more independent studies, all reporting upregulation.</li><li>`Consistent downregulation`: Two or more independent studies, all reporting downregulation.</li><li>`Conflicting evidence`: Multiple studies with divergent/opposing findings (both up- and downregulation reported).</li><li>`Single-study evidence`: Association identified in exactly one published study to date.</li></ul> |
| **Number of studies (Upregulated)** | `upregulation_studies` | Integer | Count of independent peer-reviewed studies reporting increased expression in ASD. | Non-negative integer (e.g. `0`, `1`, `2`, `3+`). |
| **Number of studies (Downregulated)** | `downregulation_studies` | Integer | Count of independent peer-reviewed studies reporting decreased expression in ASD. | Non-negative integer (e.g. `0`, `1`, `2`, `3+`). |
| **Total studies** | `total_studies` | Integer | Total count of independent expression studies investigating this miRNA in ASD. | Positive integer (equals `upregulation_studies + downregulation_studies`). |
| **StudyDetails** | `StudyDetails` | Array of Objects | Nested array of study-level metadata records (revealed by clicking the row expander). | See Section 4 (Nested Study Details Metadata). |

---

## 2. Genetic & Other Studies Table (`other_studies.json`)

Catalog of microRNAs associated with genomic structural variants, single nucleotide variations, or targeted sequencing in ASD cohorts.

| Column Header | JSON Key | Data Type | Description | Allowed / Categorical Values |
| :--- | :--- | :--- | :--- | :--- |
| **Precursor miRNA (hairpin)** | `precursor_mirna` | String (HTML Link) | Official precursor stem-loop RNA name. | Standardized to miRBase v22.1. |
| **Mature miRNA** | `mature_mirna` | String (HTML Link) | Mature functional miRNA identifier. | Standardized to miRBase v22.1. |
| **Alteration** | `alteration` | String | Categorical genomic or functional variant classification. | <ul><li>`CNV`: Copy Number Variation (e.g. microdeletions, microduplications affecting miRNA genomic loci).</li><li>`SNV`: Single Nucleotide Variant identified in whole-exome or whole-genome sequencing.</li><li>`SNP`: Single Nucleotide Polymorphism identified in candidate gene or GWAS association studies.</li><li>`miRNA expression`: Secondary targeted expression analysis in genetic variant cohorts.</li></ul> |
| **Study description** | `study_description` | String | Summary of experimental and genetic methodologies utilized. | Free text describing sequencing platform, array CGH, cohort characteristics, and locus details. |
| **StudyDetails** | `StudyDetails` | Array of Objects | Nested array of study-level metadata records. | See Section 4 (Nested Study Details Metadata). |

---

## 3. Validated Target Genes Table (`target_genes.json`)

Experimentally supported human mRNA targets of ASD-associated microRNAs, sourced from **DIANA-TarBase v9.0** and annotated with **SFARI Gene** ASD-risk susceptibility scores.

| Column Header | JSON Key | Data Type | Description | Allowed / Categorical Values |
| :--- | :--- | :--- | :--- | :--- |
| **Precursor miRNA** | `precursor_mirna` | String (Semicolon-delimited) | Genomic precursor hairpin(s) generating this mature miRNA (links to miRBase). | Semicolon-separated list of hairpins (e.g. `hsa-let-7a-1; hsa-let-7a-2`). |
| **Mature miRNA** | `mature_mirna` | String (HTML Link) | Mature microRNA targeting the gene (links to miRBase). | Standardized to miRBase v22.1. |
| **Target Gene** | `gene_symbol` | String (HTML Link) | Official HGNC gene symbol (links to GeneCards). | Standardized gene symbol (e.g. `PTEN`, `SHANK3`, `MECP2`, `AGO1`). |
| **Gene Description** | `gene_name` | String | Full descriptive name of the target protein-coding gene. | Descriptive text (e.g. `phosphatase and tensin homolog`, `SH3 and multiple ankyrin repeat domains 3`). |
| **ASD Susceptibility (SFARI)** | `sfari_score` | String | Curated autism risk tier from the SFARI Gene database. | <ul><li>`Category 1`: **High Confidence** risk genes (supported by rigorous statistical significance, typically ≥3 de novo likely gene-disrupting mutations in ASD cases).</li><li>`Category 2`: **Strong Candidate** genes (supported by 2 de novo LGD mutations or genome-wide significance).</li><li>`Category 3`: **Suggestive Evidence** genes (supported by suggestive single-study findings).</li><li>`Syndromic`: Genes associated with established genetic syndromes exhibiting high ASD penetrance (e.g. *Rett syndrome, Fragile X, Tuberous Sclerosis*).</li><li>`Non-SFARI`: Target genes not currently cataloged as primary ASD risk candidates in SFARI.</li></ul> |
| **Evidence Level** | `evidence_level` | String | Experimental validation tier classification from DIANA-TarBase v9.0. | <ul><li>`Strong Evidence`: Direct low-throughput molecular assays with targeted specificity (Luciferase Reporter, Western Blot, qPCR, Northern Blot, ELISA, etc.).</li><li>`Direct Binding (CLIP/CLASH)`: High-throughput physical RNA-protein binding assays with direct cross-linking and sequencing (HITS-CLIP, PAR-CLIP, CLASH, qCLASH, RIP-Seq, AGO-IP).</li><li>`High-Throughput Expression`: Large-scale transcriptome profiling upon miRNA overexpression/knockdown (RNA-Seq, Microarrays, sRNA-Seq).</li></ul> |
| **Experimental Methods** | `experimental_methods` | String (Semicolon-delimited) | Exact laboratory techniques used to validate the miRNA-target interaction. | Semicolon-delimited list (e.g. `Luciferase Reporter Assay; Western Blot; HITS-CLIP`). |
| **Regulation** | `regulation` | String | Observed functional regulatory effect of miRNA on target expression. | <ul><li>`Negative (Downregulation)`: miRNA represses mRNA or protein expression.</li><li>`Positive (Upregulation)`: miRNA enhances target expression or stability.</li><li>`—`: Unspecified / binding-only assay.</li></ul> |
| **Tissue / Cell Source** | `tissue` | String (Semicolon-delimited) | Biological tissue or cell line model where interaction was validated. | E.g. `Brain`, `Blood`, `HEK293`, `HeLa`, `Neural Progenitor Cells`, etc. |
| **PubMed Reference** | `pmids` | String (Semicolon-delimited) | PubMed Identifiers (PMIDs) of primary research publications (links to PubMed). | Semicolon-separated numerical PMIDs (e.g. `24312487; 20144220`). |

---

## 4. Nested Study Details Metadata (`study_details.json`)

Metadata describing the primary research publications linked to rows in the Expression and Genetic tables.

| Field Name | JSON Key | Data Type | Description | Examples |
| :--- | :--- | :--- | :--- | :--- |
| **Study** | `Study` | String | Short reference citation identifier (Author and Year). | `Seno (2011)`, `Vasu (2014)`, `Mundalil (2014)` |
| **Title / Description** | `Title` / `Description` | String | Full title of the published article or experimental methodology. | `Gene Expression Profiling of microRNAs in Autism Spectrum Disorder...` |
| **DOI** | `DOI` | String (URL) | Digital Object Identifier URL for direct publication access. | `https://doi.org/10.1016/j.gene.2011.06.017` |
| **Study Type** | `Study Type` | String | Broad classification of study focus. | `Expression`, `Genetic`, `Sequencing`, `Functional` |
| **Tissue type** | `Tissue type` | String | Primary biological tissue category. | `Brain`, `Blood`, `Saliva`, `LCLs` |
| **Tissue - subtype** | `Tissue - subtype` | String | Specific anatomical brain subregion or cell lineage. | `Cerebellum`, `Frontal Cortex`, `Peripheral Mononuclear Cells` |
| **ASD Samples** | `ASD samples` | Integer / String | Number of ASD subjects in the experimental cohort. | `28`, `55`, `120` |
| **Control Samples** | `Control samples` | Integer / String | Number of neurotypical control subjects in the comparison cohort. | `28`, `50`, `115` |
| **Country** | `Country` | String | Country of origin of the study cohort. | `USA`, `Brazil`, `China`, `Italy`, `Japan` |

---

## 5. Functional Enrichment Analysis & g:Profiler Fields

Specification of fields, statistical metrics, and parameters used in the **Functional Enrichment Analysis** dashboard powered by the **g:Profiler** REST API.

| Field / Metric | Source / Engine | Data Type | Description | Interpretation / Values |
| :--- | :--- | :--- | :--- | :--- |
| **Source** | g:Profiler | String (Badge) | Ontology or biological pathway database origin of the enriched term. | <ul><li>`GO:BP`: Gene Ontology Biological Process</li><li>`GO:MF`: Gene Ontology Molecular Function</li><li>`GO:CC`: Gene Ontology Cellular Component</li><li>`KEGG`: KEGG Pathway Database</li><li>`REAC`: Reactome Pathway Database</li><li>`HP`: Human Phenotype Ontology</li><li>`WP`: WikiPathways</li></ul> |
| **Term ID** | g:Profiler | String (Link) | Native identifier of the enriched functional term or pathway (links to official source). | Standard ontology ID (e.g. `GO:0007268`, `KEGG:04724`, `REAC:R-HSA-112316`, `HP:0000729`). |
| **Term Name** | g:Profiler | String | Human-readable name/description of the biological process, pathway, or phenotype. | Descriptive pathway name (e.g. *chemical synaptic transmission*, *glutamatergic synapse*, *Autistic behavior*). |
| **Adjusted P-Value ($p_{\text{adj}}$)** | g:Profiler | Float (Scientific) | Corrected hypergeometric overrepresentation significance value. | Default significance threshold $p_{\text{adj}} < 0.05$. Corrected via `g:SCS` (recommended for GO DAGs), Benjamini-Hochberg FDR, or Bonferroni. |
| **Overlap Ratio ($k / N$)** | g:Profiler | String / Ratio | Ratio of submitted target genes present in the term ($k$) relative to total input query size ($N$). | E.g. `25 / 120` target genes present in the specified pathway. |
| **Term Size ($|T|$)** | g:Profiler | Integer | Total number of annotated human protein-coding genes belonging to the ontology term. | Domain-wide gene count (e.g. `540` annotated genes). |
| **Intersecting Target Genes** | miR4ASD + g:Profiler | Array of Badges | List of user's query target genes that overlap with the term, annotated with SFARI risk badges. | Direct links to GeneCards with color-coded SFARI ASD-risk tags (Category 1, 2, 3, Syndromic). |
| **Significance Score** | miR4ASD Chart | Float | Scaled ranking metric computed as $-\log_{10}(p_{\text{adj}})$. | Higher scores denote greater statistical overrepresentation. |

