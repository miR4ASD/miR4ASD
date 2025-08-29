import pandas as pd

xls = pd.ExcelFile('Tabelas_resumo_para_Hugo.xlsx')
df_details = pd.read_excel(xls, 'miRNA_study_details')

# Clean column names (as in process_data.py)
def clean_col_names(df):
    cols = df.columns
    new_cols = [col.replace('\n(MIRBASE v22.1)', '').strip() for col in cols]
    df.columns = new_cols
    return df

df_details = clean_col_names(df_details)

details_rename_map = {
    'Paper': 'Study',
    'Reference (DOI)': 'DOI',
    'Study methods': 'Title'
}
df_details = df_details.rename(columns=details_rename_map)

# Print the 'Tissue type' column to inspect delimiters and content
print(df_details['Tissue type'].head(20))