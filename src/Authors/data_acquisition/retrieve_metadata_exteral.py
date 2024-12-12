import pandas as pd
from dotenv import load_dotenv
load_dotenv()

from orcid_data_utilities import retrive_authors_metadata_orcid
'''data_orcid = {
    'ORCID ID': ['0000-0002-1825-0097', '0000-0001-5109-3700', '0000-0002-8762-8444']
    }

df_orcid = pd.DataFrame(data_orcid)
data = retrive_authors_metadata_orcid(df_orcid)
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
#collector_with_orcid.to_csv('data/raw/Authors_external.csv')

