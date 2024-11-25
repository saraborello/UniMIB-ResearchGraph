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