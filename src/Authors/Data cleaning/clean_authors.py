import pandas as pd
from dotenv import load_dotenv
load_dotenv()

df = pd.read_csv("data/raw/Authors.csv")

# Count missing values
missing_count = df['Organization'].isna().sum()
print(f"The number of missing observations in the 'Organization' column is: {missing_count} out of a total of 1139.")

# Delete missing and export dataset without NaN values
df_cleaned = df.dropna(subset=['Organization']).copy()
df_cleaned.drop(columns=['Unnamed: 0'], inplace=True)
df_cleaned.set_index('ORCID ID', inplace=True)
print(f"The column set as the index is: {df_cleaned.index.name}.")
output_path = "data/processed/Authors.csv"
df_cleaned.to_csv(output_path, index=True)
print(df_cleaned.shape)
print(f"Dataset successfully saved to {output_path}.")
