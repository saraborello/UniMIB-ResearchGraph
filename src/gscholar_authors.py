import pandas as pd
from scholarly import scholarly

def find_professor_by_organization_gs(name_query, organization_keywords):
    search_query = scholarly.search_author(name_query)
    for professor in search_query:
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
                else: return print('Problem, take a look')
    return None

def update_dataset(dataset_path, organization_keywords):
    df1 = pd.read_csv(dataset_path)
    df = df1 #remove

    
    if 'H Index' not in df.columns:
        df['H Index'] = 'NA'
    if 'Citations' not in df.columns:
        df['Citations'] = 'NA'

    
    for index, row in df.iterrows():
        given_name = row['Given Name']
        family_name = row['Family Name']
        name_query = f"{given_name} {family_name}"

        print(f"Processing: {name_query}")  

        professor_info = find_professor_by_organization_gs(name_query, organization_keywords)

        if professor_info:
            df.at[index, 'H Index'] = professor_info['h_index']
            df.at[index, 'Citations'] = professor_info['citations']
            df.at[index, 'Keywords'] = ', '.join(professor_info['keywords'])

    return df

if __name__ == "__main__":
    dataset_path = "../../data/processed/professors_orcid_info2.csv" # Path to the dataset
    organization_keywords = ["bicocca", "Milano", "milan", "Bicocca", "unimib","milano",'UniMib']

    df = update_dataset(dataset_path, organization_keywords)
