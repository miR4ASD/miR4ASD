import pandas as pd

xls = pd.ExcelFile('Tabelas_resumo_para_Hugo.xlsx')
df_expression = pd.read_excel(xls, 'miRNA_expression_studies')

# Print the 'Study' column to inspect delimiters
print(df_expression['Study'].head(20))
