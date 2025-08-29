# miRNA Genes Associated with ASD

This project is a simple frontend to display information about miRNA genes associated with Autism Spectrum Disorder (ASD). The data is provided in an Excel file and is displayed in two interactive JavaScript tables on a static HTML page.

## Features

*   **Interactive Tables:** Uses the DataTables.js library to create two interactive tables with search and filter functionality.
*   **Data Processing:** A Python script (`process_data.py`) reads an Excel file, processes the data, and converts it into JSON format.
*   **Dynamic Data Loading:** The frontend loads the JSON data to populate the tables.
*   **Expandable Rows:** Each row has a button to expand and show more detailed information about the studies.
*   **Mirbase Links:** The miRNA hairpin and mature names are automatically linked to their respective pages on the Mirbase database.

## Data Source

*   **Excel File:** `Tabelas_resumo_para_Hugo.xlsx`
*   **Sheets:**
    *   `miRNA_expression_studies`: Lists miRNAs with "upregulated or downregulated" information per study.
    *   `miRNA_other_studies`: Lists miRNAs found in CNVs or SNVs, and the corresponding study.
    *   `miRNA_study_details`: Lists study details with DOI links.

## Usage

1.  **Run the data processing script:**

    ```bash
    python process_data.py
    ```

2.  **Open `index.html` in your browser.**