import pandas as pd
from dotenv import load_dotenv
load_dotenv()



if __name__ == "__main__":
    file_path = 'data/raw/papers_duplicated.csv'
    dataframe = pd.read_csv(file_path, sep=",")
    df_unique = dataframe.drop_duplicates(subset=['Title'], keep="first")

    # Esporta il dataset risultante in un nuovo file CSV
    output_path = 'data/processed/papers.csv'
    df_unique.to_csv(output_path, index=False)