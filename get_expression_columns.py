import pandas as pd

# Function to clean column names
def clean_col_names(df):
    cols = df.columns
    new_cols = [col.replace('\n(MIRBASE v22.1)', '').strip() for col in cols]
    df.columns = new_cols
    return df

# Read the Excel file
xls = pd.ExcelFile('Tabelas_resumo_para_Hugo.xlsx')

# Read the sheets into dataframes
df_expression = pd.read_excel(xls, 'miRNA_expression_studies')
df_other = pd.read_excel(xls, 'miRNA_other_studies')
df_details = pd.read_excel(xls, 'miRNA_study_details')

# Clean column names
df_expression = clean_col_names(df_expression)
df_other = clean_col_names(df_other)
df_details = clean_col_names(df_details)

# Harmonize column names
expression_rename_map = {
    'miRNA hairpin': 'miRNA_hairpin',
    'miRNA mature': 'miRNA_mature',
}
df_expression = df_expression.rename(columns=expression_rename_map)

other_rename_map = {
    'hairpin miRNA': 'miRNA_hairpin',
    'mature miRNA': 'miRNA_mature',
    'Variant Type': 'Alteration',
    'Reference': 'Study',
    'Type of study': 'Reported'
}
df_other = df_other.rename(columns=other_rename_map)

details_rename_map = {
    'Paper': 'Study',
    'Reference (DOI)': 'DOI',
    'Study methods': 'Title'
}
df_details = df_details.rename(columns=details_rename_map)

# Create a dictionary for quick DOI lookup
study_doi_map = df_details.set_index('Study')['DOI'].to_dict()

# --- Processing for miRNA_expression_studies ---
# Custom function to create multiple links for studies in a single cell
def create_multi_study_links(study_string):
    if pd.isna(study_string):
        return study_string
    studies = [s.strip() for s in str(study_string).split(';')]
    links = []
    for study in studies:
        doi = study_doi_map.get(study)
        if pd.notna(doi):
            links.append(f'<a href="{doi}" target="_blank">{study}</a>')
        else:
            links.append(study) # If no DOI, just display the study name
    return '; '.join(links)

df_expression['StudyLink'] = df_expression['Study'].apply(create_multi_study_links)


# --- Processing for miRNA_other_studies ---
# Merge with study details to get DOI (this part remains the same as it's one study per row)
df_other = pd.merge(df_other, df_details[['Study', 'DOI']], on='Study', how='left')

# Create StudyLink column with HTML link
df_other['StudyLink'] = df_other.apply(
    lambda row: f'<a href="{row["DOI"]}" target="_blank">{row["Study"]}</a>'
    if pd.notna(row['DOI']) else row['Study'], axis=1
)

# Print columns of df_expression after all processing
print(df_expression.columns)
