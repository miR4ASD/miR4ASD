# miR4ASD Data Dictionary & Column Reference

This document provides a comprehensive specification of all tables, columns, definitions, and allowed values/formats used in the **miR4ASD** database and web application.

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
   - **`docs/data_dictionary.md`**: This document—the comprehensive technical and user-facing specification defining schemas, definitions, and allowed values/formats.
   - **`process_data.py`**: The deterministic ETL pipeline that validates, harmonizes column names across Excel revisions, generates production JSON feeds, and parses `docs/data_dictionary.md` into `data_dictionary.json`.
   - **In-App Data Dictionary (`index.html` `#dictionaryAccordion`)**: The interactive, user-facing specification embedded in the Help tab of the web application.

---

## 1. Expression Studies Table (`expression_studies.json`)

This section provides information on human miRNAs identified in case-control expression studies of Autism Spectrum Disorder (ASD), including their expression patterns, sample types, and supporting evidence.

| Column name | Definition & Purpose | Allowed Values & Formats |
| :--- | :--- | :--- |
| **Precursor miRNA (hairpin)** | Name of the stem-loop precursor miRNA (hairpin), according to miRBase nomenclature (v22.1). It includes a hyperlink to the corresponding miRBase entry. | e.g. `hsa-let-7a-1`, `hsa-mir-146a`, `hsa-mir-155`. |
| **Mature miRNA** | Name of the functional, single-stranded mature miRNA derived from a precursor miRNA, according to miRBase nomenclature (v22.1). It includes a hyperlink to the corresponding miRBase entry. | e.g. `hsa-let-7a-5p`, `hsa-miR-146a-5p`, `hsa-miR-155-5p`. |
| **Expression change (ASD vs. controls)** | Direction of differential expression statistically reported in the ASD cohort versus neurotypical controls. | <span class="badge bg-success-subtle text-success border me-1"><i class="fa-solid fa-arrow-up me-1"></i>Upregulated</span> Increased expression in ASD<br><span class="badge bg-danger-subtle text-danger border mt-1 me-1"><i class="fa-solid fa-arrow-down me-1"></i>Downregulated</span> Decreased expression in ASD |
| **Sample Type** | Biological tissue, fluid, or cell type used for miRNA analysis (e.g., saliva, blood, post-mortem brain tissue [brain], neural stem cells [NSCs], olfactory mucosal stem cells [OMSCs], lymphoblastoid cell lines [LCLs], and umbilical cord). | e.g. `Blood`, `Brain`, `Saliva`, `LCLs`, `NSCs`, `OMSCs`, `Umbilical cord`. |
| **Overall evidence** | Classification of expression evidence based on the direction and consistency of miRNA dysregulation across independent ASD studies included in *miR4ASD*. | <ul class="list-unstyled mb-0 ps-0" style="line-height: 1.6;"><li class="mb-2"><span class="badge bg-success-subtle text-success border">Consistent upregulation</span> Reported in &ge;2 independent studies, with all studies showing increased expression of the miRNA.</li><li class="mb-2"><span class="badge bg-danger-subtle text-danger border">Consistent downregulation</span> Reported in &ge;2 independent studies, with all studies showing decreased expression of the miRNA.</li><li class="mb-2"><span class="badge bg-warning-subtle text-warning-emphasis border">Conflicting evidence</span> Reported in &ge;2 independent studies, with opposing directions of differential expression (both increased and decreased expression of the miRNA).</li><li><span class="badge bg-info-subtle text-info-emphasis border">Single-study evidence</span> Only one study reported altered miRNA expression in individuals with ASD, with no independent replication among the studies included in the database.</li></ul> |
| **Evidence from other studies** | Additional evidence linking the miRNA to ASD from bioinformatics or genetic studies. | <ul class="list-unstyled mb-0 ps-0" style="line-height: 1.6;"><li class="mb-2"><span class="badge bg-success-subtle text-success border me-1">Bioinformatics</span> Evidence from bioinformatics studies.</li><li class="mb-2"><span class="badge bg-info-subtle text-info border me-1">Genetics: SNP</span> Evidence from genetic association studies evaluating SNPs associated with ASD.</li><li class="mb-2"><span class="badge bg-danger-subtle text-danger border me-1">Genetics: SNV</span> Evidence from sequencing studies (WES or WGS) reporting SNVs involving miRNA genes.</li><li><span class="badge bg-warning-subtle text-warning-emphasis border me-1">Genetics: CNV</span> Evidence from genetic studies reporting CNVs involving miRNA genes.</li></ul> |
| **# up** | Number of independent peer-reviewed studies reporting upregulation of the miRNA in individuals with ASD compared with controls. | Positive integer (&ge;1) |
| **# down** | Number of independent peer-reviewed studies reporting downregulation of the miRNA in individuals with ASD compared with controls. | Positive integer (&ge;1) |
| **Total studies** | Sum of all independent expression studies evaluating this miRNA in ASD. | Positive integer (&ge;1) |

---

## 2. Genetic & Other Studies Table (`other_studies.json`)

This section provides information on human miRNAs implicated in Autism Spectrum Disorder (ASD), based on evidence from genetic and bioinformatics studies.

| Column name | Definition & Purpose | Allowed Values & Formats |
| :--- | :--- | :--- |
| **Precursor miRNA (hairpin)** | Name of the stem-loop precursor miRNA (hairpin), according to miRBase nomenclature (v22.1). It includes a hyperlink to the corresponding miRBase entry. | e.g. `hsa-mir-34a`, `hsa-mir-106b`, `hsa-mir-211`. |
| **Mature miRNA** | Name of the functional, single-stranded mature miRNA derived from a precursor miRNA, according to miRBase nomenclature (v22.1). It includes a hyperlink to the corresponding miRBase entry. | e.g. `hsa-miR-34a-5p`, `miR-106b-5p`, `hsa-miR-211-5p`. |
| **Study Type** | Classification of studies according to the type of evidence supporting the association between the miRNA and ASD. | <ul class="list-unstyled mb-0 ps-0"><li class="mb-1"><strong>Genetics:</strong> Studies in which genetic variants involving miRNA genes were analyzed in individuals with ASD.</li><li><strong>Bioinformatics:</strong> Studies in which computational approaches were used to identify, prioritize, or classify ASD-associated miRNAs based on expression data, without reporting conventional differential expression analyses.</li></ul> |
| **Variant Type** | Type of genetic variation reported within miRNA genes in individuals with ASD. | <ul class="list-unstyled mb-0 ps-0"><li class="mb-1"><strong>CNV:</strong> Copy Number Variant involving the miRNA gene, including genomic deletions and duplications.</li><li class="mb-1"><strong>SNV:</strong> Single Nucleotide Variant identified through sequencing-based studies (e.g. Whole Exome Sequencing, Whole Genome Sequencing).</li><li><strong>SNP:</strong> Single Nucleotide Polymorphism identified in genetic association studies.</li></ul> |
| **Evidence from expression studies** | Classification of expression evidence based on the direction and consistency of miRNA dysregulation across independent ASD studies included in *miR4ASD*. | <ul class="list-unstyled mb-0 ps-0"><li class="mb-1"><strong>Consistent upregulation:</strong> Reported in &ge;2 independent studies, with all studies showing increased expression of the miRNA.</li><li class="mb-1"><strong>Consistent downregulation:</strong> Reported in &ge;2 independent studies, with all studies showing decreased expression of the miRNA.</li><li class="mb-1"><strong>Conflicting evidence:</strong> Reported in &ge;2 independent studies, with opposing directions of differential expression (both increased and decreased expression of the miRNA).</li><li class="mb-1"><strong>Single-study evidence:</strong> Only one study reported altered miRNA expression in individuals with ASD, with no independent replication among the studies included in the database.</li><li><strong>None:</strong> No expression evidence is reported in the studies included in the database.</li></ul> |
| **Total expression studies** | Number of independent ASD expression studies included in the database reporting differential expression of the miRNA. | Positive integer (&ge;1) |
| **Description of expression evidence** | Detailed description of the expression evidence, including the direction of differential expression, number of independent studies, sample types analyzed, and mature miRNA-specific findings (e.g., -5p and -3p). | Free text describing the available expression evidence, including mature miRNA-specific findings when applicable; no predefined categorical values. |

---

## 3. Nested Study Details Metadata (`study_details.json`)

This section provides detailed information from the original studies included in *miR4ASD*. The information is accessible by clicking the "+" button associated with each miRNA entry in the *Expression Studies* and *Genetic and Other Studies* tabs.

| Column name | Definition & Purpose | Allowed Values & Formats |
| :--- | :--- | :--- |
| **Study** | Reference to the original publication, displayed using the first author’s surname and publication year and linked to the corresponding publication. | Author (year) format, with a hyperlink to the original publication (e.g. `Mor (2015)`, `Wu (2016)`, `Toma (2015)`). |
| **Description** | Brief description of the study, including the main experimental approach, biological sample analyzed, and miRNA-related analysis performed. | Free-text study description; no predefined categorical values. |
| **Sample Type** <span class="text-muted" style="font-size: 0.8rem;">(Tissue Type)</span> | Broad classification of the biological sample used for miRNA analysis. | e.g., `Brain`, `Blood`, `Saliva`, `Umbilical cord`, `Other`. |
| **Sample Subtype** <span class="text-muted" style="font-size: 0.8rem;">(Tissue Subtype)</span> | Specific biological material, cell type, or anatomical region analyzed within the corresponding sample type. | Free text specifying the biological material, cell type, or anatomical region analyzed (e.g., plasma, serum, whole blood, LCLs, NSCs, or specific post-mortem brain regions). |
| **Methodology** | Experimental or analytical method used to generate or analyze the data reported in the study. | e.g., `RT-qPCR`, `Small RNA-seq`, `RNA-seq`, `miRNA microarray`, `WES`, `WGS`, `SNP array`, `aCGH`. |
| **Diagnostic Tools** | Diagnostic criteria and/or standardized assessment instruments used to establish or support ASD diagnosis in study participants. | e.g. `DSM-5`, `DSM-IV`, `DSM-IV-TR`, `ADI-R`, `ADOS`, `CARS`, `ABC`, `GARS`, `SRS`. N/A indicates that diagnostic information was not available or not reported in the publication. |
| **ASD Samples** | Number of ASD samples analyzed in each study, with separate sample groups or analysis stages reported when applicable. | Number of ASD samples (*N*), reported as a single value or separately for distinct study groups, cohorts, analysis stages, or methodologies (e.g., ASN *N* = 31). |
| **Control Samples** | Number of control samples analyzed in each study, with separate sample groups or analysis stages reported when applicable. | Number of control samples (*N*), reported as a single value or separately for distinct study groups, cohorts, analysis stages, or methodologies (e.g., Control *N* = 30). |
| **Country** | Country where the study was conducted and/or population reported for the participants included in the study. | e.g., `USA`, `Brazil`, `China`, `Italy`, `Japan`. |

---

## 4. Validated Target Genes Table (`target_genes.json`)

This section contains information on experimentally validated target genes of ASD-associated miRNAs, retrieved from **miRTarBase** version 10.0. It provides miRNA-target gene interactions and their supporting experimental evidence, enabling users to explore potential regulatory relationships. Additionally, it includes **SFARI Gene** evidence classifications, indicating the strength of evidence supporting the involvement of these target genes in ASD risk.

| Column name | Definition & Purpose | Allowed Values & Formats |
| :--- | :--- | :--- |
| **Precursor miRNA** | Corresponding genomic stem-loop hairpins encoding the targeting mature miRNA. | Semicolon-separated miRBase precursor IDs. |
| **Mature miRNA** | Mature microRNA guiding target mRNA recognition (links to miRBase). | Standardized to miRBase v22.1. |
| **Target Gene** | Official HGNC Gene Symbol of the validated mRNA target (links to GeneCards). | e.g. `PTEN`, `SHANK3`, `MECP2`, `CHD8`, `AGO1`, `AGO4` |
| **Gene Description** | Full descriptive name of the target protein-coding gene. | e.g. *phosphatase and tensin homolog*, *SH3 and multiple ankyrin repeat domains 3* |
| **ASD Susceptibility (SFARI)** | Evidence category assigned to the target gene by SFARI Gene (Simons Foundation Autism Research Initiative), a database that curates genes implicated in ASD risk and classifies them according to the strength of evidence supporting their association with ASD. | <ul class="list-unstyled mb-0 ps-0"><li><span class="badge bg-danger-subtle text-danger border rounded-pill"><span class="sfari-tag sfari-tag-cat1 me-1">1</span>SFARI Category 1</span> High Confidence: Genes with strong genetic evidence supporting their association with ASD, typically including at least three <em>de novo</em> likely gene-disrupting mutations.</li><li><span class="badge border rounded-pill" style="background-color: #fef3c7; color: #92400e;"><span class="sfari-tag sfari-tag-cat2 me-1">2</span>SFARI Category 2</span> Strong Candidate: Genes supported by substantial genetic evidence, such as two <em>de novo</em> likely gene-disrupting mutations or compelling genome-wide association evidence.</li><li><span class="badge bg-info-subtle text-info border rounded-pill"><span class="sfari-tag sfari-tag-cat3 me-1">3</span>SFARI Category 3</span> Suggestive Evidence: Genes with preliminary evidence of association with ASD, such as a single <em>de novo</em> likely gene-disrupting mutation or an unreplicated association.</li><li><span class="badge border rounded-pill" style="background-color: #f3e9ff; color: #6b21a5;"><span class="sfari-tag sfari-tag-syn me-1">S</span>SFARI Syndromic</span> Genes associated with increased ASD risk and additional clinical features characteristic of a genetic syndrome.</li><li><span class="badge bg-light text-secondary border rounded-pill">None</span> Genes not listed in the SFARI Gene database.</li></ul> |
| **Database Source** | Curated database source for experimentally validated target interactions. In this version, all interactions are derived exclusively from miRTarBase 10.0 (DIANA-TarBase is no longer used). | <span class="badge bg-success-subtle text-success border px-2 py-1 rounded-pill"><i class="fa-solid fa-database me-1"></i>miRTarBase 10.0</span> |
| **Support Type** | Experimental support classification of the miRNA-target interaction from miRTarBase 10.0. | <ul class="mb-0 ps-3"><li><span class="badge bg-success-subtle text-success border rounded-pill">Functional MTI:</span> Supported by at least one functional microRNA-target interaction (Luciferase Reporter, Western Blot, qPCR, Northern Blot, ELISA, etc.).</li><li><span class="badge bg-secondary-subtle text-secondary border rounded-pill">Weak Support:</span> Supported only by weak-evidence functional interactions.</li></ul> |
| **PubMed Reference** | PubMed Identifiers (PMIDs) linking directly to the primary research articles. | Clickable PMID badges (e.g. `24312487`, `20144220`). |
| **Experiments** | Exact laboratory techniques used to confirm the miRNA-target interaction. | Semicolon-separated methods (e.g. `Luciferase reporter assay`, `Western blot`, `HITS-CLIP`, `RT-qPCR`). |

---

## 5. Functional Enrichment Analysis & g:Profiler Fields

This section allows users to perform functional enrichment analyses by selecting ASD-associated miRNAs and/or their target genes. Gene Ontology (GO) and pathway enrichment analyses are executed through the **g:Profiler** REST API, and the results are displayed on the *miR4ASD* website, highlighting enriched biological processes and pathways associated with the selected target genes.

| Column name | Definition & Purpose | Allowed Values & Formats |
| :--- | :--- | :--- |
| **Source** | Curated biological pathway or gene ontology database queried. | <span class="badge badge-source badge-gobp me-1">GO:BP</span> Biological Process<br><span class="badge badge-source badge-gomf me-1">GO:MF</span> Molecular Function<br><span class="badge badge-source badge-gocc me-1">GO:CC</span> Cellular Component<br><span class="badge badge-source badge-kegg me-1">KEGG</span> Biological Pathways<br><span class="badge badge-source badge-reac me-1">REAC</span> Reactome Pathways<br><span class="badge badge-source badge-hp me-1">HP</span> Human Phenotype Ontology<br><span class="badge badge-source badge-wp me-1">WP</span> WikiPathways |
| **Term ID** | Official ontology or pathway database identifier hyperlinking to the external source repository. | e.g. `GO:0007268`, `KEGG:04724`, `REAC:R-HSA-112316`, `HP:0000729` |
| **Term Name** | Human-readable biological process, functional cascade, or clinical phenotype description. | e.g. *chemical synaptic transmission*, *Glutamatergic synapse*, *Autistic behavior* |
| **Adjusted P-Value** | Corrected statistical significance value for hypergeometric overrepresentation. | Corrected via `g:SCS` (default), `Benjamini-Hochberg FDR`, or `Bonferroni` ($p_{\text{adj}} < 0.05$). |
| **Overlap (k/N)** | Ratio of user submitted target genes in term ($k$) relative to total submitted query size ($N$). | e.g. `25 / 120` target genes intersecting the enriched term. |
| **Term Size** | Total number of annotated human protein-coding genes belonging to this functional term. | Positive integer (e.g. `210`, `450`, `1,280`). |
| **Intersecting Target Genes** | List of user query target genes found in the term with clickable GeneCards links and SFARI autism risk confidence tiers. | Clickable GeneCards links with symbol tokens (<span class="sfari-tag sfari-tag-cat1">1</span> Cat 1, <span class="sfari-tag sfari-tag-cat2">2</span> Cat 2, <span class="sfari-tag sfari-tag-cat3">3</span> Cat 3, <span class="sfari-tag sfari-tag-syn">S</span> Syndromic, <span class="sfari-tag-group"><span class="sfari-tag sfari-tag-cat2">2</span><span class="sfari-tag sfari-tag-syn">S</span></span> Dual Status). |
| **Significance Score** <span class="badge bg-light text-secondary border ms-1" style="font-size: 0.7rem;">Bar Chart Metric</span> | Ranking metric used in Top 15 enrichment visualization charts: $-\log_{10}(p_{\text{adj}})$. | Higher values denote stronger statistical enrichment and lower false discovery rates. |

---

## 6. Experimental Methodologies Reference Table (`help_methods.json`)

Standardized molecular profiling assays, high-throughput sequencing technologies, and cytogenetic platforms used across the expression and genetic studies in miR4ASD.

| Method Abbreviation | Method | Study Type | Description |
| :--- | :--- | :--- | :--- |
| **Gene expression microarray** | Gene expression microarray | Expression | Hybridization-based technology using predefined probes to measure the relative expression levels of mRNA transcripts/genes across multiple targets simultaneously. |
| **miRNA microarray** | MicroRNA expression microarray | Expression | Hybridization-based technology using predefined probes specifically designed to detect and measure the relative expression levels of multiple mature miRNAs. |
| **RT-qPCR** | Reverse transcription-quantitative PCR | Expression | PCR-based method in which RNA is reverse-transcribed into cDNA and specific miRNAs or transcripts are quantified through real-time amplification. Includes individual, multiplex, and array-based RT-qPCR assays such as TLDA/TaqMan miRNA arrays. |
| **RNA-seq** | RNA sequencing | Expression | High-throughput sequencing of RNA-derived libraries used for transcriptome-wide characterization and quantification of RNA expression, particularly mRNA and other longer RNA transcripts. |
| **Small RNA-seq** | Small RNA sequencing | Expression | High-throughput sequencing using libraries enriched for small RNA molecules, enabling detection and quantification of miRNAs and other small non-coding RNAs. |
| **NanoString** | NanoString nCounter | Expression | Direct digital RNA detection and counting using sequence-specific barcoded probes, without enzymatic amplification. |
| **SNP array** | Single nucleotide polymorphism array | Genetics | DNA hybridization-based technology using predefined probes to genotype large numbers of SNPs across the genome. Probe intensity and allelic signals can also be used to identify copy-number variants and regions of homozygosity. |
| **WES** | Whole exome sequencing | Genetics | High-throughput DNA sequencing targeting primarily the protein-coding regions (exons) of the genome, enabling detection of SNVs and small insertions/deletions and, depending on the analytical pipeline, other variant types. |
| **WGS** | Whole genome sequencing | Genetics | High-throughput sequencing of genomic DNA across coding and non-coding regions, enabling comprehensive detection of SNVs, insertions/deletions, and, depending on the analytical pipeline, structural and copy-number variants. |
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
