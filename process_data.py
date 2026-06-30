import pandas as pd
import json
import re

def create_gff_maps(gff_file):
    """
    Parse a GFF3 file and create name-to-ID maps for miRNA hairpins and mature miRNAs.

    Parameters:
    gff_file (str): The absolute or relative path to the GFF3 file.

    Returns:
    tuple: Two dictionaries, (hairpin_map, mature_map), mapping names to their miRBase IDs.
    """
    hairpin_map = {}
    mature_map = {}
    with open(gff_file, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split('\t')
            if len(parts) == 9:
                attributes = parts[8]
                attr_dict = {}
                for attr in attributes.split(';'):
                    if not attr:
                        continue
                    if '=' in attr:
                        key, value = attr.split('=', 1)
                        attr_dict[key.strip()] = value.strip()
                
                if parts[2] == 'miRNA_primary_transcript':
                    if 'Name' in attr_dict and 'ID' in attr_dict:
                        hairpin_map[attr_dict['Name']] = attr_dict['ID']
                elif parts[2] == 'miRNA':
                    if 'Name' in attr_dict and 'ID' in attr_dict:
                        mature_map[attr_dict['Name']] = attr_dict['ID']
    return hairpin_map, mature_map

def clean_col_names(df):
    """
    Clean the column names of a DataFrame by stripping whitespace and removing extra text.

    Parameters:
    df (pandas.DataFrame): The DataFrame whose columns should be cleaned.

    Returns:
    pandas.DataFrame: The DataFrame with cleaned column names.
    """
    cols = df.columns
    new_cols = [col.replace('\n(MIRBASE v22.1)', '').strip() for col in cols]
    df.columns = new_cols
    return df

def normalize_study_name(name):
    """
    Normalize study names to match the primary keys in the study details sheet.

    Parameters:
    name (str): The raw study name extracted from the expression or other studies sheet.

    Returns:
    str: The normalized study name.
    """
    name = name.strip()
    # Resolve known spelling mismatches between sheets
    if name == 'Seno (2011)':
        return 'Ghahramani Seno (2011)'
    if name == 'Vasu (2014)':
        return 'Mundalil Vasu (2014)'
    return name

# Create the hairpin and mature maps from GFF3
hairpin_to_id_map, mature_to_id_map = create_gff_maps('hsa.gff3')

# Read the Excel file
xls = pd.ExcelFile('Tabelas_miR4ASD.xlsx')

# Read the sheets into dataframes
df_expression = pd.read_excel(xls, 'miRNA_expression_studies')
df_other = pd.read_excel(xls, 'miRNA_other_studies')
df_details = pd.read_excel(xls, 'miRNA_study_details')

# Clean column names
df_expression = clean_col_names(df_expression)
df_other = clean_col_names(df_other)
df_details = clean_col_names(df_details)

# Harmonize column names for df_details (retained rename map for future-proofing)
details_rename_map = {
    'Paper': 'Study',
    'Reference (DOI)': 'DOI',
    'Study methods': 'Title'
}
df_details = df_details.rename(columns=details_rename_map)

# Clean and strip Study names in details
df_details['Study'] = df_details['Study'].astype(str).str.strip()

# Create a dictionary for quick study details lookup
study_details_records = df_details.to_dict(orient='records')
study_details_map = {study['Study']: study for study in study_details_records}

def get_tissue_for_study(study_name, original_tissue_str):
    """
    Determine the short, standardized tissue name for a study using its details.

    Parameters:
    study_name (str): The name of the study.
    original_tissue_str (str): The original tissue string from the expression study row as a fallback.

    Returns:
    str: The short, standardized tissue name (e.g., Blood, Brain, LCLs, OMSCs, etc.).
    """
    if study_name in study_details_map:
        details = study_details_map[study_name]
        t_type = str(details.get('Tissue type', '')).strip()
        t_sub = str(details.get('Tissue - subtype', '')).strip()
        
        # Standardized short-name mappings based on the detailed study sheet
        if 'Lymphoblast' in t_sub or 'LCL' in t_sub or 'LCLs' in t_sub:
            return 'LCLs'
        elif 'Olfactory' in t_sub or 'OMSC' in t_sub or 'OMSCs' in t_sub:
            return 'OMSCs'
        elif 'Neural Stem' in t_sub or 'NSC' in t_sub or 'NSCs' in t_sub:
            return 'NSCs'
        elif t_type == 'Blood':
            return 'Blood'
        elif t_type == 'Brain':
            return 'Brain'
        elif t_type == 'Saliva':
            return 'Saliva'
        elif t_type == 'umbilical cord':
            return 'umbilical cord'
        elif 'pineal' in t_type.lower():
            return 'Blood; Brain'
            
    # Fallback to cleaning the original tissue string if details aren't found or mapped
    if pd.notna(original_tissue_str):
        # Standardize comma delimiters to semicolons
        cleaned = str(original_tissue_str).replace(',', ';')
        parts = [p.strip() for p in cleaned.split(';') if p.strip()]
        return '; '.join(parts)
    return original_tissue_str

# --- Processing for miRNA_expression_studies ---

# Standardize delimiters: replace commas acting as separators with semicolons
df_expression['Study'] = df_expression['Study'].astype(str).str.replace(r'\s*,\s*', '; ', regex=True)
df_expression['Tissue'] = df_expression['Tissue'].astype(str).str.replace(r'\s*,\s*', '; ', regex=True)

# Map details for multiple studies separated by semicolon
def get_study_details_for_expression(row):
    """Retrieve details list for all studies in the expression row."""
    study_names = [s.strip() for s in str(row['Study']).split(';')]
    details_list = []
    for study_name in study_names:
        study_name_norm = normalize_study_name(study_name)
        if study_name_norm in study_details_map:
            details_list.append(study_details_map[study_name_norm])
    return details_list

df_expression['StudyDetails'] = df_expression.apply(get_study_details_for_expression, axis=1)

# Drop redundant or temporary columns
cols_to_drop = [c for c in ['Study', 'Observations', 'Unnamed: 10'] if c in df_expression.columns]
df_expression = df_expression.drop(columns=cols_to_drop)

# Rename expression studies columns for clean JSON keys (avoid parenthesis parsing bugs in DataTables)
df_expression = df_expression.rename(columns={
    'Precursor miRNA (hairpin)': 'precursor_mirna',
    'Mature miRNA': 'mature_mirna',
    'Expression change (ASD vs. controls)': 'expression_change',
    'Tissue': 'tissue',
    'Overall evidence': 'overall_evidence',
    'Number of studies (Upregulated)': 'upregulation_studies',
    'Number of studies (Downregulated)': 'downregulation_studies',
    'Total studies': 'total_studies'
})


# --- Processing for miRNA_other_studies ---

# Standardize delimiters in other studies
df_other['Study'] = df_other['Study'].astype(str).str.replace(r'\s*,\s*', '; ', regex=True)
df_other['Study description'] = df_other['Study description'].astype(str).str.replace(r'\s*,\s*', '; ', regex=True)

# Map details for multiple studies separated by semicolon
def get_study_details_for_other(row):
    """Retrieve details list for all studies in the other row."""
    study_names = [s.strip() for s in str(row['Study']).split(';')]
    details_list = []
    for study_name in study_names:
        study_name_norm = normalize_study_name(study_name)
        if study_name_norm in study_details_map:
            details_list.append(study_details_map[study_name_norm])
    return details_list

df_other['StudyDetails'] = df_other.apply(get_study_details_for_other, axis=1)

# Drop redundant columns
df_other = df_other.drop(columns=['Study', 'Study Type'])

# Rename other studies columns for clean JSON keys (avoid parenthesis parsing bugs in DataTables)
df_other = df_other.rename(columns={
    'miRNA ID': 'precursor_mirna',
    'miRNA mature ID': 'mature_mirna',
    'Alteration': 'alteration',
    'Study description': 'study_description'
})


# --- MIRBASE ID Link Generation ---

def create_mirbase_hairpin_link(hairpin_name):
    """Generate HTML anchor for a hairpin miRNA pointing to miRBase."""
    if hairpin_name in hairpin_to_id_map:
        mirbase_id = hairpin_to_id_map[hairpin_name]
        return f'<a href="https://www.mirbase.org/hairpin/{mirbase_id}" target="_blank">{hairpin_name}</a>'
    return hairpin_name

def create_mirbase_mature_link(mature_name):
    """Generate HTML anchor for a mature miRNA pointing to miRBase."""
    if pd.isna(mature_name):
        return mature_name
    if mature_name in mature_to_id_map:
        mirbase_id = mature_to_id_map[mature_name]
        return f'<a href="https://www.mirbase.org/mature/{mirbase_id}" target="_blank">{mature_name}</a>'
    return mature_name

# Calculate unique counts on raw data before wrapping in HTML links
raw_mirna_ids = pd.concat([df_expression['precursor_mirna'], df_other['precursor_mirna']]).dropna().astype(str).str.strip()
total_mirna_genes = int(raw_mirna_ids.nunique())

raw_mature_ids = pd.concat([df_expression['mature_mirna'], df_other['mature_mirna']]).dropna().astype(str).str.strip()
total_mirna_mature = int(raw_mature_ids.nunique())

total_studies = int(df_details['Study'].nunique())

# Apply link generation to the hairpins and mature IDs
df_expression['precursor_mirna'] = df_expression['precursor_mirna'].apply(create_mirbase_hairpin_link)
df_other['precursor_mirna'] = df_other['precursor_mirna'].apply(create_mirbase_hairpin_link)

df_expression['mature_mirna'] = df_expression['mature_mirna'].apply(create_mirbase_mature_link)
df_other['mature_mirna'] = df_other['mature_mirna'].apply(create_mirbase_mature_link)


# --- Calculate and Save Statistics ---

def calculate_and_save_statistics(df_expression, df_other, total_studies, total_mirna_genes, total_mirna_mature):
    """
    Calculate summary statistics (unique counts, tissue, and alteration counts) and save as JSON.

    Parameters:
    df_expression (pandas.DataFrame): The processed expression studies.
    df_other (pandas.DataFrame): The processed genetic and other studies.
    total_studies (int): Total unique studies.
    total_mirna_genes (int): Total unique miRNA IDs.
    total_mirna_mature (int): Total unique miRNA mature IDs.
    """
    # Expression alteration counts (sum of upregulated/downregulated counts)
    alteration_counts = {
        'upregulated': int(df_expression['upregulation_studies'].sum()),
        'downregulated': int(df_expression['downregulation_studies'].sum())
    }
    
    # Standardize, split, and count individual tissues from expression studies
    tissue_counts = {}
    for tissue_str in df_expression['tissue'].dropna():
        for part in str(tissue_str).split(';'):
            part_clean = part.strip()
            if not part_clean:
                continue
            
            # Standard capitalization rules
            if part_clean.lower() == 'umbilical cord':
                part_clean = 'umbilical cord'
            else:
                part_clean = part_clean[0].upper() + part_clean[1:] if len(part_clean) > 0 else part_clean
            
            tissue_counts[part_clean] = tissue_counts.get(part_clean, 0) + 1

    stats = {
        'total_studies': total_studies,
        'total_mirna_genes': total_mirna_genes,
        'total_mirna_mature': total_mirna_mature,
        'alteration_counts': alteration_counts,
        'tissue_counts': tissue_counts
    }
    
    with open('statistics.json', 'w') as f:
        json.dump(stats, f, indent=4)


# --- Convert to JSON and Save ---

df_expression.to_json('expression_studies.json', orient='records', default_handler=str)
df_other.to_json('other_studies.json', orient='records', default_handler=str)
df_details.to_json('study_details.json', orient='records', default_handler=str)

# Save the statistics file
calculate_and_save_statistics(df_expression, df_other, total_studies, total_mirna_genes, total_mirna_mature)

print("Data processing complete. JSON files created.")
print("Expression Studies count:", len(df_expression))
print("Other Studies count:", len(df_other))
print("First Expression Study Record (JSON):")
print(json.dumps(df_expression.iloc[0].to_dict(), indent=4))
