import pandas as pd
import csv
from dotenv import load_dotenv
load_dotenv()

from orcid_data_utilities import retrive_authors_metadata_name

'''data_names = {
    'Given Name': ['Fabio','Stefania'],
    'Family Name': ['Mercorio', 'BANDINI']
}'''
df_names = pd.read_csv('data/raw/authors_inernal_short.csv')
filters = ['bicocca','milano']  # Optional filters
data = retrive_authors_metadata_name(df_names,filters)
print(data)
#pd.to_csv('data/raw/Authors_internal.csv')