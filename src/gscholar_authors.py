import pandas as pd
from scholarly import scholarly

def find_professor_by_organization_gs(name_query, organization_keywords):
    search_query = scholarly.search_author(name_query)
    count = 0
    while count < 4:  
        try:
            professor = next(search_query)
            count += 1
            professor_info = scholarly.fill(professor)
            if 'affiliation' in professor_info:
                for keyword in organization_keywords:
                    if keyword.lower() in professor_info['affiliation'].lower():
                        return {
                            "name": professor_info['name'],
                            "affiliation": professor_info['affiliation'],
                            "keywords": professor_info.get('interests', []),
                            "citations": professor_info.get('citedby', 'NA'),
                            "h_index": professor_info.get('hindex', 'NA')
                        }
            
            if 'email_domain' in professor_info:
                for keyword in organization_keywords:
                    if keyword.lower() in professor_info['email_domain'].lower() or 'campus.unimib.it' in professor_info['email_domain'].lower():
                        return {
                            "name": professor_info['name'],
                            "affiliation": professor_info.get('affiliation', 'NA'),
                            "keywords": professor_info.get('interests', []),
                            "citations": professor_info.get('citedby', 'NA'),
                            "h_index": professor_info.get('hindex', 'NA')
                        }
        except StopIteration:
            break
    print('Problem, take a look')
    return None

def update_dataset(dataset_path, organization_keywords):
    df = pd.read_csv(dataset_path)

    if 'H Index' not in df.columns:
        df['H Index'] = pd.NA
    if 'Citations' not in df.columns:
        df['Citations'] = pd.NA

    for index, row in df.iterrows():
        given_name = row['Given Name']
        family_name = row['Family Name']
        name_query = f"{given_name} {family_name}"

        print(f"Processing: {name_query}")  # Control text
        if pd.isna(row['Citations']) or row['Citations'] == '':
            professor_info = find_professor_by_organization_gs(name_query, organization_keywords)

            if professor_info:
                print(f"Updating information for: {name_query}")  # Control text
                df.at[index, 'H Index'] = professor_info['h_index']
                df.at[index, 'Citations'] = professor_info['citations']
                df.at[index, 'Keywords'] = ', '.join(professor_info['keywords'])
            else:
                print(f"No information found for: {name_query}")
        else:
            print(f"Citations already present for: {name_query}")  # Control text for already present citations

    return df

if __name__ == "__main__":
    dataset_path = "../../data/processed/professors_orcid_info2.csv" # Path to the dataset
    organization_keywords = ["bicocca", "Milano", "milan", "Bicocca", "unimib","milano",'UniMib']

    df = update_dataset(dataset_path, organization_keywords)
