import requests
import pandas as pd


def extract_department_and_name(ssd):
    if pd.isna(ssd):
        return pd.Series([None, None])

    # Controlla se il codice dipartimento termina con "/A)"
    if ssd.endswith(')'):
        # Trova l'ultima occorrenza del codice dipartimento
        split_pos = ssd.rfind('(')
        department_code = ssd[split_pos:].strip()
        specific_name = ssd[:split_pos].strip()
        return pd.Series([department_code, specific_name])
    else:
        return pd.Series([None, ssd.strip()])


def search_orcid_by_name(given_name, family_name):
    base_url = "https://pub.orcid.org/v3.0/expanded-search"
    query = f"given-names:{given_name} AND family-name:{family_name}"
    url = f"{base_url}/?q={query}"

    headers = {
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Errore durante la ricerca: {response.status_code}")
        return None


def get_orcid_profile(orcid_id):
    url = f'https://pub.orcid.org/v3.0/{orcid_id}'
    headers = {
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Errore durante il recupero del profilo: {response.status_code}")
        return None


def extract_profile_info(profile_data, orcid_id):
    if profile_data.get('person', {}).get('name', {}):
        given_names = profile_data.get('person', {}).get('name', {}).get('given-names', {}).get('value', 'N/A')
        family_name = profile_data.get('person', {}).get('name', {}).get('family-name', {}).get('value', 'N/A')

        keywords = profile_data.get('person', {}).get('keywords', {}).get('keyword', [])
        keywords_list = [kw.get('content') for kw in keywords]

        employment_summary = profile_data.get('activities-summary', {}).get('employments', {}).get('affiliation-group', [])
        if employment_summary and 'summaries' in employment_summary[0]:
            summaries = employment_summary[0].get('summaries', [])
            if summaries:
                latest_employment = summaries[0].get('employment-summary', {})
                role_title = latest_employment.get('role-title', 'N/A')
                organization_name = latest_employment.get('organization', {}).get('name', 'N/A')
            else:
                role_title = organization_name = 'N/A'
        else:
            role_title = organization_name = 'N/A'

        return {
            'Given Name': given_names,
            'Family Name': family_name,
            'Keywords': ', '.join(keywords_list) if keywords_list else 'Nessuna',
            'Role Title': role_title,
            'Organization': organization_name,
            'ORCID ID': orcid_id
        }

    return None

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
