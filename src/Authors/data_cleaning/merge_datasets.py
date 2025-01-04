import pandas as pd

def merge_datasets(df1, df2, missing_value="none"):
    
    merged = pd.concat([df1, df2], ignore_index=True)
    merged = merged.fillna(missing_value)
    
    return merged

df1 = pd.read_csv('data/raw/Authors_internal.csv')
df2 = pd.read_csv('data/raw/authors_external_final_updated.csv.csv')
result = merge_datasets(df1, df2, missing_value="none")
result.to_csv('data/raw/Authors_updated.csv')
