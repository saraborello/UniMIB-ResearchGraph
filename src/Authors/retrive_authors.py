import requests
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

from orcid_data_utilities import get_orcid_profile, extract_profile_info, search_orcid_by_name


def retrive_authors_metadata_orcid(authors_df: pd.DataFrame):

    authors_df = authors_df.assign(Given_Name=None, Family_Name=None, Role=None,
                            Keywords=None, Organization=None)

    for index, row in authors_df.iterrows():
        orcid_id = row['ORCID ID']
        response = get_orcid_profile(orcid_id)
        if not response:
            continue
        print(orcid_id)
        result = extract_profile_info(response, orcid_id)
        if result:
            authors_df.at[index, 'Given_Name'] = result['Given Name']
            authors_df.at[index, 'Family_Name'] = result['Family Name']
            authors_df.at[index, 'Organization'] = result['Organization']
            authors_df.at[index, 'Role'] = result['Role Title']
            authors_df.at[index, 'Keywords'] = result['Keywords']
        else:
            authors_df = authors_df.drop(index=index)

    return authors_df


def retrive_authors_metadata_name(authors_df: pd.DataFrame, filters: list):

    authors_df = authors_df.assign(ORCID_ID = None, Role=None,
                            Keywords=None, Organization=None)

    for index, row in authors_df.iterrows():
        given_name = row['Given Name']
        family_name = row['Family Name']

        response = search_orcid_by_name(given_name, family_name)
        print(response)
        if response and 'expanded-result' in response:
            for result in response['expanded-result']:
                orcid_id = result.get('orcid-id')
                profile_data = get_orcid_profile(orcid_id)
                if not profile_data:
                    print(f"No results for {given_name} {family_name}")
                else:
                    result = extract_profile_info(profile_data, orcid_id)

                    if result:
                        organization = result['Organization'].lower()
                        if any(f in organization for f in filters):
                            authors_df.at[index, 'ORCID_ID'] = orcid_id
                            authors_df.at[index, 'Organization'] = organization
                            authors_df.at[index, 'Role'] = result['Role Title']
                            authors_df.at[index, 'Keywords'] = result['Keywords']
                        print(result)
                    else:
                        authors_df = authors_df.drop(index=index)
        else:
            continue

    return authors_df


if __name__ == "__main__":

    # Example with dataset containing only ORCID IDs
    '''data_orcid = {
        'ORCID ID': ['0000-0002-1825-0097', '0000-0001-5109-3700', '0000-0002-8762-8444']
    }
    df_orcid = pd.DataFrame(data_orcid)
    data = retrive_authors_metadata_orcid(df_orcid)
    print(data)'''

    # Example with dataset containing only names
    '''data_names = {
        'Given Name': ['Fabio','Stefania'],
        'Family Name': ['Mercorio', 'BANDINI']
    }
    df_names = pd.DataFrame(data_names)
    filters = ['bicocca','milano']  # Optional filters
    data = retrive_authors_metadata_name(df_names,filters)
    print(data)'''

    authors = pd.read_csv('data/processed/Authors.csv')
    papers = pd.read_csv('data/processed/papers.csv')
    list_a = authors['ORCID ID'].tolist()  # Prima lista
    list_b = papers['Authors'].tolist()
    all_authors = [author.strip() for authors in list_b for author in authors.split(',')]
    unique_authors = list(set(all_authors))
    list_b = unique_authors

    set_a = set(list_a)
    set_b = set(list_b)

    only_in_a = set_a - set_b
    only_in_b = set_b - set_a

    print("Elementi presenti solo in 'a':", len(only_in_a))
    print("Elementi presenti solo in 'b':", len(only_in_b))

    df_orcid = pd.DataFrame(only_in_b, columns=['ORCID ID']).dropna()
    collector_with_orcid = retrive_authors_metadata_orcid(df_orcid)
    collector_with_orcid.to_csv('data/processed/Authors_new.csv')