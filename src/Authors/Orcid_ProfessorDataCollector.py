import requests
import pandas as pd

class ProfessorDataCollector:
    def __init__(self, csv_file_path_or_df, organization_filters=None):
        if isinstance(csv_file_path_or_df, pd.DataFrame):
            self.df = csv_file_path_or_df
        else:
            self.df = pd.read_csv(csv_file_path_or_df)
        self.organization_filters = [f.lower() for f in organization_filters] if organization_filters else []

    def collect_professor_data(self):
        # Initialize DataFrame columns
        self.initialize_dataframe()

        for index, row in self.df.iterrows():
            given_name, family_name, orcid_id = self.extract_professor_basic_info(row)

            if pd.notna(orcid_id):
                self.handle_existing_orcid(index, orcid_id)
            elif given_name and family_name:
                self.handle_name_search(index, given_name, family_name)

    def initialize_dataframe(self):
        """
        Initialize the DataFrame with required columns.
        """
        self.df = self.df.assign(ORCID_ID=None, Organization=None, Status=None, Role_Title=None,
                                 Start_Date=None, Keywords=None, Number_of_Works=None, Given_Name=None, Family_Name=None)

    def extract_professor_basic_info(self, row):
        """
        Extract given name, family name, and ORCID ID from a DataFrame row.

        Args:
            row (pd.Series): The DataFrame row.

        Returns:
            tuple: given name, family name, ORCID ID
        """
        given_name = row.get('Given Name')
        family_name = row.get('Family Name')
        orcid_id = row.get('ORCID ID')
        return given_name, family_name, orcid_id

    def handle_existing_orcid(self, index, orcid_id):
        """
        Handle data extraction for professors with an existing ORCID ID.

        Args:
            index (int): The DataFrame row index.
            orcid_id (str): The ORCID ID.
        """
        profile_data = self.get_orcid_profile(orcid_id)
        prof_info = self.extract_profile_info(profile_data, orcid_id)
        if prof_info:
            self.update_professor_info(index, prof_info, 'APPROVED')
        else:
            self.df.at[index, 'Status'] = 'TO CHECK'

    def handle_name_search(self, index, given_name, family_name):
        """
        Handle ORCID search by given name and family name.

        Args:
            index (int): The DataFrame row index.
            given_name (str): The given name of the professor.
            family_name (str): The family name of the professor.
        """
        print(f"DEBUG: Searching ORCID for given name: {given_name}, family name: {family_name}")
        search_results = self.search_orcid_by_name(given_name, family_name)
        print(f"DEBUG: Search results: {search_results}")

        if not search_results or 'expanded-result' not in search_results or not search_results['expanded-result']:
            print(f"DEBUG: No valid search results found for {given_name} {family_name}")
            self.df.at[index, 'Status'] = 'TO CHECK'
            return

        for result in search_results['expanded-result']:
            if not result:
                continue
            orcid_id = result.get('orcid-id')
            print(f"DEBUG: Found ORCID ID: {orcid_id}")
            profile_data = self.get_orcid_profile(orcid_id)
            print(f"DEBUG: Profile data for ORCID ID {orcid_id}: {profile_data}")
            prof_info = self.extract_profile_info(profile_data, orcid_id)
            if not prof_info:
                print(f"DEBUG: No valid profile info for ORCID ID {orcid_id}")
                continue

            if self.is_valid_organization(prof_info['Organization']):
                print(f"DEBUG: Valid organization found: {prof_info['Organization']}")
                self.update_professor_info(index, prof_info, 'APPROVED')
                break


    def is_valid_organization(self, organization_name):
        """
        Check if the organization name matches any of the organization filters.

        Args:
            organization_name (str): The name of the organization.

        Returns:
            bool: True if the organization matches the filters or if no filters are set.
        """
        organization_name = organization_name.lower()
        return not self.organization_filters or any(f in organization_name for f in self.organization_filters)

    def update_professor_info(self, index, prof_info, status):
        """
        Update the DataFrame with professor information.

        Args:
            index (int): The DataFrame row index.
            prof_info (dict): The extracted professor information.
            status (str): The status to be assigned ('APPROVED' or 'TO CHECK').
        """
        self.df.loc[index, ['ORCID_ID', 'Organization', 'Role_Title', 'Start_Date',
                            'Keywords', 'Number_of_Works', 'Given_Name', 'Family_Name', 'Status']] = [
            prof_info['ORCID ID'], prof_info['Organization'], prof_info['Role Title'],
            prof_info['Start Date'], prof_info['Keywords'], prof_info['Number of Works'],
            prof_info['Given Name'], prof_info['Family Name'], status
        ]

    @staticmethod
    def search_orcid_by_name(given_name, family_name):
        """
        Search for an ORCID profile by given name and family name.

        Args:
            given_name (str): The first name of the individual.
            family_name (str): The last name of the individual.

        Returns:
            dict or None: The JSON response with ORCID profile data if successful, or None if the request fails.
        """
        url = f"https://pub.orcid.org/v3.0/expanded-search/?q=given-names:{given_name} AND family-name:{family_name}"
        headers = {'Accept': 'application/json'}
        response = requests.get(url, headers=headers)
        return response.json() if response.status_code == 200 else None

    @staticmethod
    def get_orcid_profile(orcid_id):
        """
        Retrieve an ORCID profile by ORCID ID.

        Args:
            orcid_id (str): The unique ORCID identifier.

        Returns:
            dict or None: The JSON response with ORCID profile data if successful, or None if the request fails.
        """
        url = f'https://pub.orcid.org/v3.0/{orcid_id}'
        headers = {'Accept': 'application/json'}
        response = requests.get(url, headers=headers)
        return response.json() if response.status_code == 200 else None

    @staticmethod
    def extract_profile_info(profile_data, orcid_id):
        """
        Extract profile information from ORCID profile data.

        Args:
            profile_data (dict): The JSON data of the ORCID profile.
            orcid_id (str): The ORCID identifier.

        Returns:
            dict or None: A dictionary containing extracted profile information, or None if required data is missing.
                        The returned information includes given name, family name, keywords, latest role title, start date,
                        organization name, number of works, and the ORCID ID.
        """
        if not profile_data:
            return None

        try:
            # Extracting name information with fallback handling
            name_info = profile_data.get('person', {}).get('name') or {}
            given_names = name_info.get('given-names', {}).get('value') if isinstance(name_info, dict) else None
            family_name = name_info.get('family-name', {}).get('value') if isinstance(name_info, dict) else None

            # If either given name or family name is missing, return None
            if not given_names or not family_name:
                return None

            # Extracting keywords with fallback handling
            keywords = profile_data.get('person', {}).get('keywords', {}).get('keyword', []) or []
            keywords_list = [kw.get('content', 'N/A') for kw in keywords if isinstance(kw, dict)]

            # Extracting employment information with fallback handling
            employment = profile_data.get('activities-summary', {}).get('employments', {}).get('affiliation-group', []) or []
            latest_employment = employment[0].get('summaries', [])[0].get('employment-summary', {}) if employment and employment[0].get('summaries') else {}

            role_title = latest_employment.get('role-title', 'N/A')
            start_date_info = latest_employment.get('start-date', {}) or {}
            start_date = start_date_info.get('year', {}).get('value', 'N/A')
            start_date = start_date if start_date else 'N/A'
            organization_name = latest_employment.get('organization', {}).get('name', 'N/A')

            # Extracting works count with fallback handling
            num_works = len(profile_data.get('activities-summary', {}).get('works', {}).get('group', []) or [])

            return {
                'Given Name': given_names,
                'Family Name': family_name,
                'Keywords': ', '.join(keywords_list) if keywords_list else 'N/A',
                'Role Title': role_title,
                'Start Date': start_date,
                'Organization': organization_name,
                'Number of Works': num_works,
                'ORCID ID': orcid_id
            }

        except AttributeError as e:
            # Log the error (optional) and continue
            print(f"Skipping ORCID {orcid_id} due to an error: {e}")
            return None

# Example usage
if __name__ == "__main__":
    # Example with dataset containing only ORCID IDs
    '''data_orcid = {
        'ORCID ID': ['0000-0002-1825-0097', '0000-0001-5109-3700', '0000-0003-1613-5470']
    }
    df_orcid = pd.DataFrame(data_orcid)
    collector_with_orcid = ProfessorDataCollector(df_orcid)
    collector_with_orcid.collect_professor_data()
    print(collector_with_orcid.df)'''

    # Example with dataset containing only names
    data_names = {
        'Given Name': ['Fabio','Stefania'],
        'Family Name': ['Mercorio', 'BANDINI']
    }
    df_names = pd.DataFrame(data_names)
    filters = ['Bicocca']  # Optional filters
    collector_with_names = ProfessorDataCollector(df_names, organization_filters=filters)
    collector_with_names.collect_professor_data()
    print(collector_with_names.df)
