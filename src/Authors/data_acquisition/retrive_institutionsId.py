import pandas as pd
import json
from dotenv import load_dotenv
load_dotenv()
import os

csv_path = "data/raw/Authors_external_final.csv"
dict_path = "data/raw/organization_to_openalex.json"


df = pd.read_csv(csv_path)
with open(dict_path, 'r') as f:
    institutions_dict = json.load(f)


df['institutions_id'] = df['institution'].map(institutions_dict)

df.to_csv("data/raw/authors_external_final_updated.csv", index=False)


