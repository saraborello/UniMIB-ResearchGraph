
import requests
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


def extract_profile_info1(profile_data, orcid_id):
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
    if employment_summary and 'summaries' in employment_summary[0]:
        summaries = employment_summary[0].get('summaries', [])
        if summaries:
            latest_employment = summaries[0].get('employment-summary', {})
            role_title = latest_employment.get('role-title', 'N/A')
            
            # Safer handling of start-date and year
            start_date_data = latest_employment.get('start-date')
            if start_date_data and isinstance(start_date_data, dict):
                year_data = start_date_data.get('year')
                start_date = year_data.get('value') if year_data and isinstance(year_data, dict) else 'N/A'
            else:
                start_date = 'N/A'

            organization_name = latest_employment.get('organization', {}).get('name', 'N/A')
        else:
            role_title = start_date = organization_name = 'N/A'
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
                    prof_info = extract_profile_info1(profile_data, orcid_id)
                    professors_info.append(prof_info)
        else:
            print(f"No results for {given_name} {family_name}")

    return professors_info


'''def collect_professor_data12(professors_df):
    professors_info = []
    not_found_professors = []

    # Extract information for each professor
    for index, row in professors_df.iterrows():
        given_name = row['Given Name']
        family_name = row['Family Name']
        print(f"Processing professor: {given_name} {family_name}")
        
        search_results = search_orcid_by_name(given_name, family_name)
        
        # Check if search_results is valid before iterating
        if search_results and isinstance(search_results, dict) and 'expanded-result' in search_results:
            try:
                found_valid_org = False
                for result in search_results['expanded-result']:
                    orcid_id = result.get('orcid-id')
                    profile_data = get_orcid_profile(orcid_id)
                    if profile_data:
                        prof_info = extract_profile_info1(profile_data, orcid_id)

                        # Check if organization contains "Bicocca", "Milan" or "Milano" (case insensitive)
                        organization_name = prof_info.get('Organization', '').lower()
                        if 'bicocca' in organization_name or 'milan' in organization_name or 'milano' in organization_name:
                            # Add professor info and set flag to True
                            professors_info.append(prof_info)
                            found_valid_org = True
                            print(f"Added professor: {given_name} {family_name} with organization {prof_info['Organization']}")
                            break  # Move to next professor once a valid organization is found

                # If no result with a valid organization was found, add to not found list
                if not found_valid_org:
                    not_found_professors.append(f"{given_name} {family_name}")
                    print(f"No organization with 'Bicocca', 'Milan', or 'Milano' found for {given_name} {family_name}")

            except TypeError as e:
                print(f"Errore durante l'iterazione dei risultati per {given_name} {family_name}: {e}")
                not_found_professors.append(f"{given_name} {family_name}")
        else:
            print(f"No results or invalid response for {given_name} {family_name}")
            not_found_professors.append(f"{given_name} {family_name}")

    return professors_info, not_found_professors'''


def collect_professor_data13(professors_df):
    loop_counter= 0
    professors_info = []
    not_found_professors = []

    # Extract information for each professor
    for index, row in professors_df.iterrows():
        loop_counter += 1
        print(f"Loop count: {loop_counter}")
        
        if loop_counter > len(professors_df):  # Imposta un limite per evitare un ciclo infinito durante il debug
            print("Exceeded loop limit, breaking to prevent infinite loop.")
            break
        given_name = row['Given Name']
        family_name = row['Family Name']
        print(f"Processing professor: {given_name} {family_name}")
        
        search_results = search_orcid_by_name(given_name, family_name)
        
        # Check if search_results is valid before iterating
        if search_results and isinstance(search_results, dict) and 'expanded-result' in search_results:
            try:
                found_valid_org = False
                for result in search_results['expanded-result']:
                    orcid_id = result.get('orcid-id')
                    profile_data = get_orcid_profile(orcid_id)
                    if profile_data:
                        prof_info = extract_profile_info1(profile_data, orcid_id)

                        # Check if organization contains "Bicocca", "Milan" or "Milano" (case insensitive)
                        organization_name = prof_info.get('Organization', '').lower()
                        if 'bicocca' in organization_name or 'milan' in organization_name or 'milano' in organization_name:
                            # Add professor info and set flag to True
                            professors_info.append(prof_info)
                            found_valid_org = True
                            print(f"Added professor: {given_name} {family_name} with organization {prof_info['Organization']}")
                            break  # Move to next professor once a valid organization is found

                # If no result with a valid organization was found, add to not found list
                if not found_valid_org:
                    not_found_professors.append(f"{given_name} {family_name}")
                    print(f"No organization with 'Bicocca', 'Milan', or 'Milano' found for {given_name} {family_name}")

            except TypeError as e:
                print(f"Errore durante l'iterazione dei risultati per {given_name} {family_name}: {e}")
                not_found_professors.append(f"{given_name} {family_name}")
        else:
            print(f"No results or invalid response for {given_name} {family_name}")
            not_found_professors.append(f"{given_name} {family_name}")

    # Debugging to ensure function ends correctly
    print("Finished processing all professors.")

    return professors_info, not_found_professors

def collect_professor_data1(professors_df):
    loop_counter = 0
    professors_info = []
    not_found_professors = []

    # Extract information for each professor
    for index, row in professors_df.iterrows():
        loop_counter += 1
        print(f"Loop count: {loop_counter}")
        
        if loop_counter > len(professors_df):  # Imposta un limite per evitare un ciclo infinito durante il debug
            print("Exceeded loop limit, breaking to prevent infinite loop.")
            break
        given_name = row['Given Name']
        family_name = row['Family Name']
        print(f"Processing professor: {given_name} {family_name}")
        
        search_results = search_orcid_by_name(given_name, family_name)
        
        # Check if search_results is valid before iterating
        if search_results and isinstance(search_results, dict) and 'expanded-result' in search_results:
            try:
                found_valid_org = False
                first_na_prof_info = None  # Per tenere traccia del primo risultato 'N/A'

                for result in search_results['expanded-result']:
                    orcid_id = result.get('orcid-id')
                    profile_data = get_orcid_profile(orcid_id)
                    if profile_data:
                        prof_info = extract_profile_info1(profile_data, orcid_id)

                        # Check if organization contains "Bicocca", "Milan" or "Milano" (case insensitive)
                        organization_name = prof_info.get('Organization', '').lower()
                        if 'bicocca' in organization_name or 'milan' in organization_name or 'milano' in organization_name:
                            # Add professor info and set flag to True
                            professors_info.append(prof_info)
                            found_valid_org = True
                            print(f"Added professor: {given_name} {family_name} with organization {prof_info['Organization']}")
                            break  # Move to next professor once a valid organization is found

                        # Se non c'è una corrispondenza, memorizza il primo risultato 'N/A'
                        if first_na_prof_info is None:
                            first_na_prof_info = prof_info

                # Se non è stata trovata un'organizzazione valida, aggiungi il primo risultato 'N/A'
                if not found_valid_org and first_na_prof_info:
                    professors_info.append(first_na_prof_info)
                    print(f"Added professor: {given_name} {family_name} with organization {first_na_prof_info['Organization']} (no valid match found)")

                # If no result with a valid organization was found, add to not found list
                if not found_valid_org and not first_na_prof_info:
                    not_found_professors.append(f"{given_name} {family_name}")
                    print(f"No organization with 'Bicocca', 'Milan', or 'Milano' found for {given_name} {family_name}")

            except TypeError as e:
                print(f"Errore durante l'iterazione dei risultati per {given_name} {family_name}: {e}")
                not_found_professors.append(f"{given_name} {family_name}")
        else:
            print(f"No results or invalid response for {given_name} {family_name}")
            not_found_professors.append(f"{given_name} {family_name}")

    # Debugging to ensure function ends correctly
    print("Finished processing all professors.")

    return professors_info, not_found_professors
