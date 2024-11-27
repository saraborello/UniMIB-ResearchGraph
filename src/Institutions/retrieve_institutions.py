import pandas as pd
import requests
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

class UniversityInfoUpdater:
    def __init__(self, dataset, llm_token):
        self.dataset = dataset
        self.llm_token = llm_token
        self.corrected_names_dict = {}
        genai.configure(api_key=llm_token)
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')

    def find_institution_on_openalex(self, institution_name):
        base_url = "https://api.openalex.org/"
        endpoint = "institutions"
        params = {"filter": f"display_name.search:{institution_name}"}
        response = requests.get(f"{base_url}{endpoint}", params=params)
        if response.status_code == 200:
            data = response.json()
            if "results" in data and len(data["results"]) > 0:
                return data["results"][0]  
        return None

    def extract_correct_university_name(self, text):
        directions_prompt = f"""
        rewrite only the correct name of the university in a correct form in english 
        Text: {text} """
        json_text = self.model.generate_content(directions_prompt).text
        return json_text

    def update_dataset(self):
        
        for index, row in self.dataset.iterrows():
            institution_name = row['Institution']
            print(f"Processing: {institution_name}")
            
           
            institution_info = self.find_institution_on_openalex(institution_name)
            
            if institution_info:
                
                self.dataset.at[index, 'openalex_id'] = institution_info['id']
                self.dataset.at[index, 'country'] = institution_info.get('country_code', 'N/A')
                self.dataset.at[index, 'type'] = institution_info.get('type', 'N/A')
                self.dataset.at[index, 'homepage_url'] = institution_info.get('homepage_url', 'N/A')
                self.dataset.at[index, 'works_count'] = institution_info.get('works_count', 'N/A')
                self.dataset.at[index, 'cited_by_count'] = institution_info.get('cited_by_count', 'N/A')
            else:
                correct_name = self.extract_correct_university_name(institution_name)
                self.corrected_names_dict[institution_name] = correct_name
                print(f"Corrected '{institution_name}' to '{correct_name}'")
                
                
                institution_info = self.find_institution_on_openalex(correct_name)
                if institution_info:
                    self.dataset.at[index, 'openalex_id'] = institution_info['id']
                    self.dataset.at[index, 'country'] = institution_info.get('country_code', 'N/A')
                    self.dataset.at[index, 'type'] = institution_info.get('type', 'N/A')
                    self.dataset.at[index, 'homepage_url'] = institution_info.get('homepage_url', 'N/A')
                    self.dataset.at[index, 'works_count'] = institution_info.get('works_count', 'N/A')
                    self.dataset.at[index, 'cited_by_count'] = institution_info.get('cited_by_count', 'N/A')

    def save_corrected_names(self, filename):
        with open(filename, 'w') as file:
            for wrong_name, correct_name in self.corrected_names_dict.items():
                file.write(f"{wrong_name} -> {correct_name}\n")

    def get_updated_dataset(self):
        return self.dataset

# Example usage
authors =  pd.read('../../data/raw/authors_external')
istitutions_df = pd.DataFrame(authors['Institution'].unique())
dataset = istitutions_df.loc[10:40]

llm_token = api_key=os.getenv("GEMINIKEY")
updater = UniversityInfoUpdater(dataset, llm_token)
updater.update_dataset()
updated_dataset = updater.get_updated_dataset()
updated_dataset
