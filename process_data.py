import pandas as pd
import json
import csv

# Function to parse the GFF3 file and create a name to ID map
def create_gff_maps(gff_file):
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
                    key, value = attr.split('=')
                    attr_dict[key] = value
                
                if parts[2] == 'miRNA_primary_transcript':
                    if 'Name' in attr_dict and 'ID' in attr_dict:
                        hairpin_map[attr_dict['Name']] = attr_dict['ID']
                elif parts[2] == 'miRNA':
                    if 'Name' in attr_dict and 'ID' in attr_dict:
                        mature_map[attr_dict['Name']] = attr_dict['ID']
    return hairpin_map, mature_map

# Function to clean column names
def clean_col_names(df):
    cols = df.columns
    new_cols = [col.replace('\n(MIRBASE v22.1)', '').strip() for col in cols]
    df.columns = new_cols
    return df

# Create the hairpin and mature maps
hairpin_to_id_map, mature_to_id_map = create_gff_maps('hsa.gff3')

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

# Harmonize column names for df_details (still needed)
details_rename_map = {
    'Paper': 'Study',
    'Reference (DOI)': 'DOI',
    'Study methods': 'Title'
}
df_details = df_details.rename(columns=details_rename_map)

# Create a dictionary for quick study details lookup
study_details_records = df_details.to_dict(orient='records')
study_details_map = {study['Study']: study for study in study_details_records}

# --- Processing for miRNA_expression_studies ---
def get_study_details_for_expression(row):
    study_names = [s.strip() for s in str(row['Study']).split(';')]
    details_list = []
    for study_name in study_names:
        if study_name in study_details_map:
            details_list.append(study_details_map[study_name])
    return details_list

df_expression['StudyDetails'] = df_expression.apply(get_study_details_for_expression, axis=1)
df_expression = df_expression.drop(columns=['Study'])

# Function to parse 'Number of studies down or upregulated'
def parse_up_down_studies(text):
    up = 0
    down = 0
    if isinstance(text, str):
        parts = text.lower().replace(',', '').split(' ')
        for i, part in enumerate(parts):
            if part == 'up' and i > 0 and parts[i-1].isdigit():
                up = int(parts[i-1])
            elif part == 'down' and i > 0 and parts[i-1].isdigit():
                down = int(parts[i-1])
    return up, down

df_expression[['# studies upregulation', '# studies downregulation']] = df_expression['Number of studies down or upregulated'].apply(lambda x: pd.Series(parse_up_down_studies(x)))

df_expression = df_expression.drop(columns=['Number of studies down or upregulated', 'Observations', 'Unnamed: 9'])

# --- Processing for miRNA_other_studies ---
def get_study_details_for_other(row):
    study_name = row['Study']
    if study_name in study_details_map:
        return [study_details_map[study_name]]
    return []

df_other['StudyDetails'] = df_other.apply(get_study_details_for_other, axis=1)
df_other = df_other.drop(columns=['Study', 'Study Type'])

# Function to create mirbase links
def create_mirbase_hairpin_link(hairpin_name):
    if hairpin_name in hairpin_to_id_map:
        mirbase_id = hairpin_to_id_map[hairpin_name]
        return f'<a href="https://www.mirbase.org/hairpin/{mirbase_id}" target="_blank">{hairpin_name}</a>'
    return hairpin_name

def create_mirbase_mature_link(mature_name):
    if pd.isna(mature_name):
        return mature_name
    if mature_name in mature_to_id_map:
        mirbase_id = mature_to_id_map[mature_name]
        return f'<a href="https://www.mirbase.org/mature/{mirbase_id}" target="_blank">{mature_name}</a>'
    return mature_name

# Apply the link creation to the dataframes
df_expression['miRNA ID'] = df_expression['miRNA ID'].apply(create_mirbase_hairpin_link)
df_other['miRNA ID'] = df_other['miRNA ID'].apply(create_mirbase_hairpin_link)

df_expression['miRNA mature ID'] = df_expression['miRNA mature ID'].apply(create_mirbase_mature_link)
df_other['miRNA mature ID'] = df_other['miRNA mature ID'].apply(create_mirbase_mature_link)

# Convert to JSON
df_expression.to_json('expression_studies.json', orient='records', default_handler=str)
df_other.to_json('other_studies.json', orient='records', default_handler=str)
df_details.to_json('study_details.json', orient='records', default_handler=str)

print("Data processing complete. JSON files created.")
print("Expression Studies Head:")
print(df_expression.head())
print("\nFirst Expression Study Record (JSON):")
print(json.dumps(df_expression.iloc[0].to_dict(), indent=4))
print("\nOther Studies Head:")
print(df_other.head())
print("\nStudy Details Head:")
print(df_details.head())
