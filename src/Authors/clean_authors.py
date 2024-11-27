import pandas as pd
from dotenv import load_dotenv
load_dotenv()

df = pd.read_csv("data/processed/Authors_updated.csv")

# Count missing values
missing_count = df['Organization'].isna().sum()
print(f"Il numero di osservazioni mancanti nella colonna 'Organization' è: {missing_count} su un totale di 1139")

# Delete missing and export dataset without na
df_cleaned = df.dropna(subset=['Organization']).copy()
df_cleaned.drop(columns=['Unnamed: 0'], inplace=True)
df_cleaned.set_index('ORCID ID', inplace=True)
print(f"La colonna impostata come indice è: {df_cleaned.index.name}")
output_path = "data/processed/Authors_updated_nona.csv"
df_cleaned.to_csv(output_path, index=True)
print(df_cleaned.shape)
print(f"Dataset salvato con successo in {output_path}")