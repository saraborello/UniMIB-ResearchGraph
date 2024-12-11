import pandas as pd
from scholarly import scholarly
import csv

def find_professor(name_query, organization_keywords=None):
    """Search for a professor using name, with optional filtering by organization keywords."""
    search_query = scholarly.search_author(name_query)
    for _ in range(4):  # Limit to 4 results
        try:
            professor_info = scholarly.fill(next(search_query))
            if organization_keywords:
                affiliation = professor_info.get('affiliation', '').lower()
                email_domain = professor_info.get('email_domain', '').lower()
                if not any(k.lower() in affiliation or k.lower() in email_domain for k in organization_keywords):
                    continue  # Skip if no keyword match
            return {
                "name": professor_info['name'],
                "affiliation": professor_info.get('affiliation', 'NA'),
                "keywords": professor_info.get('interests', []),
                "citations": professor_info.get('citedby', 'NA'),
                "h_index": professor_info.get('hindex', 'NA')
            }
        except StopIteration:
            break
        except Exception as e:
            print(f"Error processing {name_query}: {e}")
    return None

def update_dataset(dataset_path, organization_keywords=None):
    """Update dataset with professor information from Google Scholar."""
    df = pd.read_csv(dataset_path)
    for col in ['H Index', 'Citations', 'Keywords', 'Organization']:
        df[col] = df.get(col, pd.NA)

    for index, row in df.iterrows():
        if not any(pd.isna(row[col]) for col in ['Citations', 'H Index', 'Keywords', 'Organization']):
            print(f"Skipping: {row['Given Name']} {row['Family Name']}, data already present.")
            continue

        name_query = f"{row['Given Name']} {row['Family Name']}"
        print(f"Processing: {name_query}")
        professor_info = find_professor(name_query, organization_keywords)
        if professor_info:
            df.loc[index, ['H Index', 'Citations', 'Keywords', 'Organization']] = [
                professor_info['h_index'], 
                professor_info['citations'], 
                ', '.join(professor_info['keywords']), 
                professor_info['affiliation']
            ]
        else:
            print(f"No information found for: {name_query}")
    return df

if __name__ == "__main__":
    dataset_path = "data/raw/Authors.csv"
    organization_keywords = ["bicocca", "milano", "unimib"]  # Set to None to disable filtering

    updated_df = update_dataset(dataset_path, organization_keywords)
    updated_df.to_csv("data/raw/Authors.csv", index=False, quoting=csv.QUOTE_NONNUMERIC)