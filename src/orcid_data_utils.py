
import requests
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
    given_names = profile_data.get('person', {}).get('name', {}).get('given-names', {}).get('value', 'N/A')
    family_name = profile_data.get('person', {}).get('name', {}).get('family-name', {}).get('value', 'N/A')

    keywords = profile_data.get('person', {}).get('keywords', {}).get('keyword', [])
    keywords_list = [kw.get('content') for kw in keywords]

    external_ids = profile_data.get('person', {}).get('external-identifiers', {}).get('external-identifier', [])
    researcher_id = None
    for ext_id in external_ids:
        if ext_id.get('external-id-type') == 'ResearcherID':
            researcher_id = ext_id.get('external-id-value')
            break

    employment_summary = profile_data.get('activities-summary', {}).get('employments', {}).get('affiliation-group', [])
    if employment_summary:
        latest_employment = employment_summary[0].get('summaries', [])[0].get('employment-summary', {})
        role_title = latest_employment.get('role-title', 'N/A')
        start_date = latest_employment.get('start-date', {}).get('year', {}).get('value', 'N/A')
        organization_name = latest_employment.get('organization', {}).get('name', 'N/A')
    else:
        role_title = start_date = organization_name = 'N/A'

    works_total = profile_data.get('activities-summary', {}).get('works', {}).get('group', [])
    num_works = len(works_total)

    return {
        'Given Name': given_names,
        'Family Name': family_name,
        'Keywords': ', '.join(keywords_list) if keywords_list else 'Nessuna',
        'ResearcherID': researcher_id if researcher_id else 'N/A',
        'Role Title': role_title,
        'Start Date': start_date,
        'Organization': organization_name,
        'Number of Works': num_works,
        'ORCID ID': orcid_id
    }

def collect_professor_data(professors_df):
    professors_info = []

    # Estrai tutte le informazioni per ciascun professore
    for index, row in professors_df.iterrows():
        given_name = row['Given Name']
        family_name = row['Family Name']
        search_results = search_orcid_by_name(given_name, family_name)

        if search_results and 'expanded-result' in search_results:
            for result in search_results['expanded-result']:
                orcid_id = result.get('orcid-id')
                profile_data = get_orcid_profile(orcid_id)
                if profile_data:
                    prof_info = extract_profile_info(profile_data, orcid_id)
                    professors_info.append(prof_info)
        else:
            print(f"No results for {given_name} {family_name}")

    return professors_info


