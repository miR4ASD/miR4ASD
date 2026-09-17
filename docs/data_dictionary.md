# miR4ASD Data Dictionary & Column Reference

This document provides a comprehensive specification of all tables, columns, data types, sources, and categorical enumeration values used in the **miR4ASD** database and web application.

---

## Sources of Truth for the Data Dictionary

The miR4ASD data dictionary is governed by a multi-tier hierarchy of authoritative sources:

1. **Primary Curated Research Workbooks (Upstream Clinical & Experimental Curation)**
   - **`raw_data/Tabelas_miR4ASD(site)_15.09.2026.xlsx`**: The definitive upstream workbook maintained by the research team containing three core sheets:
     - `miRNA_expression_studies`: Curated microRNA differential expression findings in ASD versus neurotypical controls, standardized sample types, directional deregulation, and publication tallies.
     - `miRNA_other_studies`: Curated genomic variants (CNVs, SNVs, SNPs) impacting microRNA loci, along with cross-study expression evidence.
     - `miRNA_study_details`: Publication-level clinical and methodological metadata including cohort sizes (ASD and Control sample counts), diagnostic instruments (DSM-5, ADOS, ADI-R, CARS, etc.), experimental methods, sample types/subtypes, and DOI links.
   - **`Tables_for_help_tab.xlsx`**: Authoritative definitions and standardized descriptions for molecular profiling methodologies (`help_methods.json`) and clinical diagnostic tools (`help_diagnostic_tools.json`).

2. **External Curated Reference Databases (Target Validations & Biological Ontologies)**
   - **miRTarBase 10.0 (`raw_data/hsa_MTI.csv`)**: Sole authoritative external reference database for experimentally validated miRNA-target interactions (functional reporter assays, Western blots, qPCR, CLIP-Seq). *Note: DIANA-TarBase is no longer used in this version.*
   - **SFARI Gene (`raw_data/sfari_genes.csv`)**: Authoritative autism risk gene repository providing curated risk tiers (Category 1 High Confidence, Category 2 Strong Candidate, Category 3 Suggestive Evidence, and Syndromic).
   - **miRBase v22.1 (`hsa.gff3`)**: Definitive genomic coordinates, accession IDs (MI / MIMAT), and stem-loop hairpin precursor / mature miRNA nomenclature.
   - **g:Profiler REST API**: Live functional enrichment query engine computing corrected hypergeometric overrepresentation statistics across Gene Ontology (GO:BP, GO:MF, GO:CC), KEGG, Reactome, and Human Phenotype Ontology.

3. **In-Repository Technical & Application Specifications (Operational Source of Truth)**
   - **`docs/data_dictionary.md`**: This document—the comprehensive technical specification defining data models, JSON schemas, column headers, and value domains.
   - **`process_data.py`**: The deterministic ETL pipeline that validates, harmonizes column names across Excel version revisions (e.g. `Sample Type` / `Tissue`, `Sample type` / `Tissue type`), verifies data integrity, and generates production JSON feeds.
   - **In-App Data Dictionary (`index.html` `#dictionaryAccordion`)**: The interactive, user-facing specification embedded in the Help tab of the web application.

---

## 1. Expression Studies Table (`expression_studies.json`)

This section provides information on human miRNAs identified in case-control expression studies of Autism Spectrum Disorder (ASD), including their expression patterns, sample types, and supporting evidence.

| Column Header | JSON Key | Data Type | Description | Allowed / Categorical Values |
| :--- | :--- | :--- | :--- | :--- |
| **Precursor miRNA (hairpin)** | `precursor_mirna` | String (HTML Link) | Official miRBase stem-loop precursor RNA name (links to miRBase). | Standardized to miRBase v22.1 (e.g. `hsa-let-7a-1`, `hsa-mir-146a`). |
| **Mature miRNA** | `mature_mirna` | String (HTML Link) | Fully processed, functional single-stranded mature miRNA identifier. | Standardized to miRBase v22.1 (e.g. `hsa-let-7a-5p`, `hsa-miR-146a-5p`). |
| **Expression change (ASD vs. controls)** | `expression_change` | String | Reported direction of expression alteration in ASD patients compared to neurotypical controls. | <ul><li>`Upregulated`: Statistically significant increased expression in ASD cohort.</li><li>`Downregulated`: Statistically significant decreased expression in ASD cohort.</li></ul> |
| **Sample Type / Tissue** | `tissue` / `sample_type` | String (Semicolon-delimited) | Biological tissue, fluid, or cell type used for miRNA analysis (e.g., saliva, blood, post-mortem brain tissue [brain], neural stem cells [NSCs], olfactory mucosal stem cells [OMSCs], lymphoblastoid cell lines [LCLs], and umbilical cord; standardized as "Sample Type" in dataset v15.09.2026; mapped to `tissue` and `sample_type` in JSON). | e.g. `Blood`, `Brain`, `Saliva`, `LCLs`, `NSCs`, `OMSCs`, `Umbilical cord`. |
| **Overall evidence** | `overall_evidence` | String | Classification of expression evidence based on the direction and consistency of miRNA dysregulation across independent ASD studies included in *miR4ASD*. | <ul><li class="mb-1"><strong>Consistent upregulation:</strong> Reported in &ge;2 independent studies, with all studies showing increased expression of the miRNA.</li><li class="mb-1"><strong>Consistent downregulation:</strong> Reported in &ge;2 independent studies, with all studies showing decreased expression of the miRNA.</li><li class="mb-1"><strong>Conflicting evidence:</strong> Reported in &ge;2 independent studies, with opposing directions of differential expression (both increased and decreased expression of the miRNA).</li><li><strong>Single-study evidence:</strong> Only one study reported altered miRNA expression in individuals with ASD, with no independent replication among the studies included in the database.</li></ul> |
| **Evidence from other studies** | `evidence_from_other_studies` | String | Additional evidence linking the miRNA to ASD from bioinformatics or genetic studies. | <ul><li class="mb-1"><strong>Bioinformatics:</strong> Evidence from bioinformatics studies.</li><li class="mb-1"><strong>Genetics: SNP:</strong> Evidence from genetic association studies evaluating SNPs associated with ASD.</li><li class="mb-1"><strong>Genetics: SNV:</strong> Evidence from sequencing studies (WES or WGS) reporting SNVs involving miRNA genes.</li><li><strong>Genetics: CNV:</strong> Evidence from genetic studies reporting CNVs involving miRNA genes.</li></ul> |
| **# up** | `upregulation_studies` | Integer | Number of independent peer-reviewed studies reporting upregulation of the miRNA in individuals with ASD compared with controls. | Positive integer (&ge;1). |
| **# down** | `downregulation_studies` | Integer | Number of independent peer-reviewed studies reporting downregulation of the miRNA in individuals with ASD compared with controls. | Positive integer (&ge;1). |
| **Total studies** | `total_studies` | Integer | Total number of independent ASD expression studies evaluating the miRNA. | Positive integer (&ge;1). |
| **StudyDetails** | `StudyDetails` | Array of Objects | Nested array of study-level metadata records (revealed by clicking the row expander). | See Section 3 (Nested Study Details Metadata). |

---

## 2. Genetic & Other Studies Table (`other_studies.json`)

This section provides information on human miRNAs implicated in Autism Spectrum Disorder (ASD), based on evidence from genetic and bioinformatics studies.

| Column Header | JSON Key | Data Type | Description | Allowed / Categorical Values |
| :--- | :--- | :--- | :--- | :--- |
| **Precursor miRNA (hairpin)** | `precursor_mirna` | String (HTML Link) | Name of the stem-loop precursor miRNA (hairpin), according to miRBase nomenclature (v22.1). It includes a hyperlink to the corresponding miRBase entry. | e.g. `hsa-mir-34a`, `hsa-mir-106b`, `hsa-mir-211`. |
| **Mature miRNA** | `mature_mirna` | String (HTML Link) | Name of the functional, single-stranded mature miRNA derived from a precursor miRNA, according to miRBase nomenclature (v22.1). It includes a hyperlink to the corresponding miRBase entry. | e.g. `hsa-miR-34a-5p`, `miR-106b-5p`, `hsa-miR-211-5p`. |
| **Study Type** | `study_type` | String | Classification of studies according to the type of evidence supporting the association between the miRNA and ASD. | <ul><li class="mb-1"><strong>Genetics:</strong> Studies in which genetic variants involving miRNA genes were analyzed in individuals with ASD.</li><li><strong>Bioinformatics:</strong> Studies in which computational approaches were used to identify, prioritize, or classify ASD-associated miRNAs based on expression data, without reporting conventional differential expression analyses.</li></ul> |
| **Variant Type** | `variant_type` | String | Type of genetic variation reported within miRNA genes in individuals with ASD. | <ul><li class="mb-1"><strong>CNV:</strong> Copy Number Variant involving the miRNA gene, including genomic deletions and duplications.</li><li class="mb-1"><strong>SNV:</strong> Single Nucleotide Variant identified through sequencing-based studies (e.g. Whole Exome Sequencing, Whole Genome Sequencing).</li><li><strong>SNP:</strong> Single Nucleotide Polymorphism identified in genetic association studies.</li></ul> |
| **Evidence from expression studies** | `evidence_from_expression_studies` | String | Classification of expression evidence based on the direction and consistency of miRNA dysregulation across independent ASD studies included in *miR4ASD*. | <ul><li class="mb-1"><strong>Consistent upregulation:</strong> Reported in &ge;2 independent studies, with all studies showing increased expression of the miRNA.</li><li class="mb-1"><strong>Consistent downregulation:</strong> Reported in &ge;2 independent studies, with all studies showing decreased expression of the miRNA.</li><li class="mb-1"><strong>Conflicting evidence:</strong> Reported in &ge;2 independent studies, with opposing directions of differential expression (both increased and decreased expression of the miRNA).</li><li class="mb-1"><strong>Single-study evidence:</strong> Only one study reported altered miRNA expression in individuals with ASD, with no independent replication among the studies included in the database.</li><li><strong>None:</strong> No expression evidence is reported in the studies included in the database.</li></ul> |
| **Total expression studies** | `total_expression_studies` | Integer | Number of independent ASD expression studies included in the database reporting differential expression of the miRNA. | Positive integer (&ge;1). |
| **Description of expression evidence** | `description_of_expression_evidence` | String | Detailed description of the expression evidence, including the direction of differential expression, number of independent studies, sample types analyzed, and mature miRNA-specific findings (e.g., -5p and -3p). | Free text describing the available expression evidence, including mature miRNA-specific findings when applicable; no predefined categorical values. |
| **StudyDetails** | `StudyDetails` | Array of Objects | Nested array of study-level metadata records. | See Section 3 (Nested Study Details Metadata). |

---

## 3. Nested Study Details Metadata (`study_details.json`)

This section provides detailed information from the original studies included in *miR4ASD*.

| Field Name | JSON Key | Data Type | Description | Examples |
| :--- | :--- | :--- | :--- | :--- |
| **Study** | `Study` | String | Short reference citation identifier (Author and Year). | `Seno (2011)`, `Vasu (2014)`, `Mundalil (2014)` |
| **Description** | `Description` | String | Full title of the published article or experimental methodology. | `Gene Expression Profiling of microRNAs in Autism Spectrum Disorder...` |
| **DOI** | `DOI` | String (URL) | Digital Object Identifier URL for direct publication access. | `https://doi.org/10.1016/j.gene.2011.06.017` |
| **Sample Type (Tissue Type)** | `Sample type` / `Tissue type` | String | Primary biological specimen or tissue analyzed (standardized as "Sample type" in v15.09.2026; mapped to both keys in JSON). | `Brain`, `Blood`, `Saliva`, `LCLs` |
| **Sample Subtype (Tissue Subtype)** | `Sample subtype` / `Tissue - subtype` | String | Specific anatomical brain subregion or refined cellular fraction (standardized as "Sample subtype" in v15.09.2026; mapped to both keys in JSON). | `Cerebellum`, `Frontal Cortex`, `Peripheral Mononuclear Cells`, `Whole Blood`, `Plasma` |
| **Methodology** | `Methodology` | String | Experimental platform or molecular assay used for profiling or quantification. Includes multi-assay platforms. | `RT-qPCR`, `Small RNA-seq`, `miRNA microarray`, `WES`, `WGS`, `SNP array`, `SNP array and WES`, `miRNA microarray and RT-qPCR`, `aCGH` |
| **Diagnostic tools** | `Diagnostic tools` | String | Diagnostic criteria or clinical behavioral instruments used for cohort diagnosis. | `DSM-5`, `ADOS`, `ADI-R`, `CARS`, `DSM-IV-TR`, `GARS`, `ABC`, `SRS` |
| **ASD Samples** | `ASD samples` | Integer / String | Number of ASD subjects in the experimental cohort. In multi-cohort studies (e.g. discovery vs. replication cohorts, or distinct tissues), values are separated by semicolons (`;`) and rendered as distinct badges/pills in the UI. | `ASD N = 12`, `Microarray ASD N = 5; RT-qPCR ASD N = 15`, `Training set ASD N = 188; Test set ASD N = 50`, `GWAS ASD N = 7387; meta-analysis replication set 1 ASD N = 7783; meta-analysis replication set 2 ASD N = 1369` |
| **Control Samples** | `Control samples` | Integer / String | Number of neurotypical control subjects in the comparison cohort. In multi-cohort studies, values are separated by semicolons (`;`) and rendered as distinct badges/pills in the UI. | `Control N = 12`, `Microarray control N = 5; RT-qPCR control N = 15`, `Training set control N = 113; Test set control N = 21` |
| **Country** | `Country` | String | Country of origin of the study cohort. | `USA`, `Brazil`, `China`, `Italy`, `Japan` |

---

## 4. Validated Target Genes Table (`target_genes.json`)

This section contains information on experimentally validated target genes of ASD-associated miRNAs, retrieved from **miRTarBase** version 10.0. It provides miRNA-target gene interactions and their supporting experimental evidence, enabling users to explore potential regulatory relationships between ASD-associated miRNAs and their target genes.

| Column Header | JSON Key | Data Type | Description | Allowed / Categorical Values |
| :--- | :--- | :--- | :--- | :--- |
| **Precursor miRNA** | `precursor_mirna` | String (Semicolon-delimited) | Genomic precursor hairpin(s) generating this mature miRNA (links to miRBase). | Semicolon-separated list of hairpins (e.g. `hsa-let-7a-1; hsa-let-7a-2`). |
| **Mature miRNA** | `mature_mirna` | String (HTML Link) | Mature microRNA targeting the gene (links to miRBase). | Standardized to miRBase v22.1. |
| **Target Gene** | `gene_symbol` | String (HTML Link) | Official HGNC gene symbol (links to GeneCards). | Standardized gene symbol (e.g. `PTEN`, `SHANK3`, `MECP2`, `AGO1`). |
| **Gene Description** | `gene_name` | String | Full descriptive name of the target protein-coding gene. | Descriptive text (e.g. `phosphatase and tensin homolog`, `SH3 and multiple ankyrin repeat domains 3`). |
| **ASD Susceptibility (SFARI)** | `sfari_score` | String | Curated autism risk tier from the SFARI Gene database. | <ul><li>`Category 1`: **High Confidence** risk genes (supported by rigorous statistical significance, typically ≥3 de novo likely gene-disrupting mutations in ASD cases).</li><li>`Category 2`: **Strong Candidate** genes (supported by 2 de novo LGD mutations or genome-wide significance).</li><li>`Category 3`: **Suggestive Evidence** genes (supported by suggestive single-study findings).</li><li>`Syndromic`: Genes associated with established genetic syndromes exhibiting high ASD penetrance (e.g. *Rett syndrome, Fragile X, Tuberous Sclerosis*).</li><li>`Non-SFARI`: Target genes not currently cataloged as primary ASD risk candidates in SFARI.</li></ul> |
| **Support Type** | `support_type` | String | Experimental support classification of the miRNA-target interaction from miRTarBase 10.0. | <ul><li>`Functional MTI`: Backed by at least one functional microRNA-target interaction (Luciferase Reporter, Western Blot, qPCR, Northern Blot, ELISA, etc.).</li><li>`Weak Support`: Backed only by weak-evidence functional interactions.</li></ul> |
| **Database Source** | `database_source` | String | Curated database origin establishing experimental validation. | `miRTarBase 10.0` (Sole validated target interaction source in this version; DIANA-TarBase is no longer used). |
| **Experiments** | `experimental_methods` | String (Semicolon-delimited) | Exact laboratory techniques used to validate the miRNA-target interaction. | Semicolon-delimited list (e.g. `Luciferase reporter assay; Western blot; HITS-CLIP`). |
| **PubMed Reference** | `pmids` | String (Semicolon-delimited) | PubMed Identifiers (PMIDs) of primary research publications (links to PubMed). | Semicolon-separated numerical PMIDs (e.g. `24312487; 20144220`). |

---

## 5. Functional Enrichment Analysis & g:Profiler Fields

This section allows users to perform functional enrichment analyses by selecting ASD-associated miRNAs and/or their target genes. Gene Ontology (GO) and pathway enrichment analyses are executed through the **g:Profiler** REST API, and the results are displayed on the *miR4ASD* website, highlighting enriched biological processes and pathways associated with the selected target genes.

| Field / Metric | Source / Engine | Data Type | Description | Interpretation / Values |
| :--- | :--- | :--- | :--- | :--- |
| **Source** | g:Profiler | String (Badge) | Ontology or biological pathway database origin of the enriched term. | <ul><li>`GO:BP`: Gene Ontology Biological Process</li><li>`GO:MF`: Gene Ontology Molecular Function</li><li>`GO:CC`: Gene Ontology Cellular Component</li><li>`KEGG`: KEGG Pathway Database</li><li>`REAC`: Reactome Pathway Database</li><li>`HP`: Human Phenotype Ontology</li><li>`WP`: WikiPathways</li></ul> |
| **Term ID** | g:Profiler | String (Link) | Native identifier of the enriched functional term or pathway (links to official source). | Standard ontology ID (e.g. `GO:0007268`, `KEGG:04724`, `REAC:R-HSA-112316`, `HP:0000729`). |
| **Term Name** | g:Profiler | String | Human-readable name/description of the biological process, pathway, or phenotype. | Descriptive pathway name (e.g. *chemical synaptic transmission*, *glutamatergic synapse*, *Autistic behavior*). |
| **Adjusted P-Value ($p_{\text{adj}}$)** | g:Profiler | Float (Scientific) | Corrected hypergeometric overrepresentation significance value. | Default significance threshold $p_{\text{adj}} < 0.05$. Corrected via `g:SCS` (recommended for GO DAGs), Benjamini-Hochberg FDR, or Bonferroni. |
| **Overlap (k/N)** | g:Profiler | String / Ratio | Ratio of submitted target genes present in the term ($k$) relative to total input query size ($N$). | E.g. `25 / 120` target genes present in the specified pathway. |
| **Term Size ($\|T\|$)** | g:Profiler | Integer | Total number of annotated human protein-coding genes belonging to the ontology term. | Domain-wide gene count (e.g. `540` annotated genes). |
| **Intersecting Target Genes** | miR4ASD + g:Profiler | Array of Badges | List of user's query target genes that overlap with the term, annotated with SFARI risk badges. | Direct links to GeneCards with color-coded SFARI ASD-risk tags (Category 1, 2, 3, Syndromic). |
| **Significance Score** | miR4ASD Chart | Float | Scaled ranking metric computed as $-\log_{10}(p_{\text{adj}})$. | Higher scores denote greater statistical overrepresentation. |

---

## 6. Experimental Methodologies Reference Table (`help_methods.json`)

Standardized molecular profiling assays, high-throughput sequencing technologies, and cytogenetic platforms used across the expression and genetic studies in miR4ASD.

| Method Abbreviation | Method Name | Study Type | Description |
| :--- | :--- | :--- | :--- |
| **Gene expression microarray** | Gene expression microarray | Expression | Hybridization-based technology using predefined probes to measure the relative expression levels of mRNA transcripts/genes across multiple targets simultaneously. |
| **miRNA microarray** | MicroRNA expression microarray | Expression | Hybridization-based technology using predefined probes specifically designed to detect and measure the relative expression levels of multiple mature miRNAs. |
| **RT-qPCR** | Reverse transcription-quantitative PCR | Expression | PCR-based method in which RNA is reverse-transcribed into cDNA and specific miRNAs or transcripts are quantified through real-time amplification. Includes individual, multiplex, and array-based RT-qPCR assays such as TLDA/TaqMan miRNA arrays. |
| **RNA-seq** | RNA sequencing | Expression | High-throughput sequencing of RNA-derived libraries used for transcriptome-wide characterization and quantification of RNA expression, particularly mRNA and other longer RNA transcripts. |
| **Small RNA-seq** | Small RNA sequencing | Expression | High-throughput sequencing using libraries enriched for small RNA molecules, enabling detection and quantification of miRNAs and other small non-coding RNAs. |
| **NanoString** | NanoString nCounter | Expression | Direct digital RNA detection and counting using sequence-specific barcoded probes, without enzymatic amplification. |
| **SNP array** | Single nucleotide polymorphism array | Genetics | DNA hybridization-based technology using predefined probes to genotype large numbers of SNPs across the genome. Probe intensity and allelic signals can also be used to identify copy-number variants and regions of homozygosity. |
| **WES** | Whole-exome sequencing | Genetics | High-throughput DNA sequencing targeting primarily the protein-coding regions (exons) of the genome, enabling detection of SNVs and small insertions/deletions and, depending on the analytical pipeline, other variant types. |
| **WGS** | Whole-genome sequencing | Genetics | High-throughput sequencing of genomic DNA across coding and non-coding regions, enabling comprehensive detection of SNVs, insertions/deletions, and, depending on the analytical pipeline, structural and copy-number variants. |
| **aCGH** | Array comparative genomic hybridization | Genetics | DNA hybridization-based technology comparing test and reference DNA across genomic probes to identify copy-number gains and losses, including genomic deletions and duplications. |

---

## 7. Clinical Diagnostic Tools Reference Table (`help_diagnostic_tools.json`)

Standardized clinical diagnostic criteria, structured interview schedules, and behavioral rating scales reported across included publications to characterize ASD cohorts.

| Diagnostic Tool / Abbreviation | Full Name & Description |
| :--- | :--- |
| **DSM-5** | Diagnostic and Statistical Manual of Mental Disorders 5th Edition |
| **DSM-IV** | Diagnostic and Statistical Manual of Mental Disorders 4th Edition |
| **DSM-IV-TR** | Diagnostic and Statistical Manual of Mental Disorders 4th Edition Text Revision |
| **ADI-R** | Autism Diagnostic Interview-Revised |
| **ADOS** | Autism Diagnostic Observation Schedule |
| **CARS** | Childhood Autism Rating Scale |
| **ABC** | Autism Behavior Scale |
| **GARS** | Gilliam Autism Rating Scale |
| **SRS** | Social Responsiveness Scale |


