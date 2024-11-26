import pandas as pd
from scholarly import scholarly
import csv

def find_professor_by_name(name_query):
    search_query = scholarly.search_author(name_query)
    try:
        professor = next(search_query)  # Prende il primo risultato
        professor_info = scholarly.fill(professor)
        return {
            "name": professor_info.get('name', 'NA'),
            "affiliation": professor_info.get('affiliation', 'NA'),
            "keywords": professor_info.get('interests', []),
            "citations": professor_info.get('citedby', 'NA'),
            "h_index": professor_info.get('hindex', 'NA'),
        }
    except StopIteration:
        print(f"No results found for {name_query}.")
    except Exception as e:
        print(f"Error processing {name_query}: {e}")
    return None

def update_dataset_by_name(authors_df: pd.DataFrame):

    for col in ['H Index', 'Citations']:
        if col not in authors_df.columns:
            authors_df[col] = None

    for index, row in authors_df.iterrows():
        given_name = row['Given_Name']
        family_name = row['Family_Name']
        name_query = f"{given_name} {family_name}"
        print(f"Processing: {name_query}") 

        # Cerca informazioni solo se `Keywords` o `Organization` è `NA` o se `H Index` e `Citations` sono vuoti
        if pd.isna(row['Keywords']) or pd.isna(row['Organization']) or pd.isna(row['H Index']) or pd.isna(row['Citations']):
            professor_info = find_professor_by_name(name_query)
            if professor_info:
                print(f"Updating information for: {name_query}")
                if pd.isna(row['Keywords']):
                    authors_df.at[index, 'Keywords'] = ', '.join(professor_info['keywords'])
                if pd.isna(row['Organization']):
                    authors_df.at[index, 'Organization'] = professor_info['affiliation']
                authors_df.at[index, 'H Index'] = professor_info['h_index']
                authors_df.at[index, 'Citations'] = professor_info['citations']
            else:
                print(f"No information found for: {name_query}")
        else:
            print(f"Skipping: {name_query}, data already present.")

    return authors_df

if __name__ == "__main__":
    dataset_path = "data/processed/Authors_new.csv"  # Percorso al dataset
    authors_df = pd.read_csv(dataset_path)
    updated_df = update_dataset_by_name(authors_df[0:200])
    updated_df.to_csv('data/processed/Authors_updated.csv', index=False, quoting=csv.QUOTE_NONNUMERIC)

