import pandas as pd
import requests
from typing import List, Optional

class AuthorInstitutionExtractor:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def search_author(self, author_name: str) -> Optional[List[dict]]:
        """Search for an author on OpenAlex using the given name."""
        search_url = f"https://api.openalex.org/authors?filter=display_name.search:{author_name}"
        response = requests.get(search_url)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('results', [])
        else:
            print(f"Error searching for author {author_name}")
            return None

    def verify_orcid(self, results: List[dict], orcid: str) -> Optional[str]:
        """Verify that the ORCID in the results matches the given ORCID."""
        for result in results:
            author_orcid = result.get('orcid')
            if author_orcid and author_orcid.split("/")[-1] == orcid:
                return result['id']  # Return the matching author's ID
        return None

    def get_past_institutions(self, author_id: str) -> Optional[List[str]]:
        """Retrieve past institutions for the author with the given ID."""
        author_url = f"https://api.openalex.org/{author_id}"
        author_response = requests.get(author_url)
        
        if author_response.status_code == 200:
            author_data = author_response.json()
            current_year = 2024
            # Extract past institutions as those not including the current year
            past_institutions = [
                affiliation["institution"]["display_name"]
                for affiliation in author_data.get("affiliations", [])
                if current_year not in affiliation["years"]
            ]
            return past_institutions
        else:
            print(f"Error retrieving details for author with ID {author_id}")
            return None

    def process_author(self, given_name: str, family_name: str, orcid: str) -> Optional[List[str]]:
        """Run the full process to find past institutions for an author."""
        author_name = f"{given_name} {family_name}"
        results = self.search_author(author_name)
        
        if results:
            author_id = self.verify_orcid(results, orcid)
            if author_id:
                return self.get_past_institutions(author_id)
            else:
                print(f"Author with ORCID {orcid} not found.")
                return None
        else:
            return None

    def add_past_institutions_column(self, start_index: Optional[int] = None, end_index: Optional[int] = None) -> pd.DataFrame:
        """Add a column of past institutions to the DataFrame for a subset of rows.
        
        Args:
            start_index (int): The starting index for updating rows.
            end_index (Optional[int]): The ending index for updating rows. If None, updates to the end of the DataFrame.
        """
        # Default start and end indices if not provided
        if start_index is None:
            start_index = 0
        if end_index is None:
            end_index = len(self.df)
        
        # Apply only to the specified range of rows
        self.df.loc[start_index:end_index, 'Past Institutions'] = self.df.loc[start_index:end_index].apply(
            lambda row: self.process_author(
                row['Given Name'], row['Family Name'], row['ORCID ID']
            ),
            axis=1
        )
        return self.df


'''df = pd.read_csv('../../data/processed/Authors.csv')
extractor = AuthorInstitutionExtractor(df)

# Set start and end indices as variables (debugging)
start_index = 0
end_index = len(df)

updated_df = extractor.add_past_institutions_column(start_index=start_index, end_index=end_index)
updated_df.to_csv('../../data/processed/Authors_inst.csv')'''

