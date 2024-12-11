import pandas as pd
import requests
from typing import List, Optional

def search_author(author_name: str) -> Optional[List[dict]]:
    search_url = f"https://api.openalex.org/authors?filter=display_name.search:{author_name}"
    response = requests.get(search_url)
    if response.status_code == 200:
        data = response.json()
        return data.get('results', [])
    return None

def verify_orcid(results: List[dict], orcid: str) -> Optional[str]:
    for result in results:
        author_orcid = result.get('orcid')
        if author_orcid and author_orcid.split("/")[-1] == orcid:
            return result['id']
    return None

def get_past_institutions(author_id: str) -> Optional[List[str]]:
    author_url = f"https://api.openalex.org/{author_id}"
    author_response = requests.get(author_url)
    if author_response.status_code == 200:
        author_data = author_response.json()
        current_year = 2024
        past_institutions = [
            affiliation["institution"]["display_name"]
            for affiliation in author_data.get("affiliations", [])
            if current_year not in affiliation["years"]
        ]
        return past_institutions
    return None

def process_author(given_name: str, family_name: str, orcid: str) -> Optional[List[str]]:
    author_name = f"{given_name} {family_name}"
    results = search_author(author_name)
    if results:
        author_id = verify_orcid(results, orcid)
        if author_id:
            return get_past_institutions(author_id)
    return None

def add_past_institutions_column(df: pd.DataFrame, start_index: Optional[int] = None, end_index: Optional[int] = None) -> pd.DataFrame:
    if start_index is None:
        start_index = 0
    if end_index is None:
        end_index = len(df)
    df.loc[start_index:end_index, 'Past Institutions'] = df.loc[start_index:end_index].apply(
        lambda row: process_author(
            row['Given Name'], row['Family Name'], row['ORCID ID']
        ),
        axis=1
    )
    return df

df = pd.read_csv('../../data/raw/Authors_internal.csv')
start_index = 0
end_index = len(df)
updated_df = add_past_institutions_column(df, start_index=start_index, end_index=end_index)
updated_df.to_csv('../../data/raw/Authors_internal.csv')
