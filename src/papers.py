import csv

import pandas as pd
import requests

from orcid_data_utils import get_orcid_profile




def get_contributors_from_crossref(doi: str) -> list[str]:
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        authors = data.get("message", {}).get("author", [])
        author_names = [f"{author.get('given')} {author.get('family')}" for author in authors]
        return author_names
    else:
        print(f"Could not retrieve authors using crossref for the paper with doi {doi}")
        return [""]


def get_papers_metainformation_staff(orcid: str) -> list[str]:

    papers = []
    response_profile = get_orcid_profile(orcid)
    if response_profile:
        works = response_profile.get('activities-summary', {}).get('works', {}).get('group', [])
        for work in works:
            for summary in work.get('work-summary', []):
                doi = None
                url = None
                for ext_id in summary.get('external-ids', {}).get('external-id', []):
                    if ext_id.get('external-id-type') == 'doi':
                        doi = ext_id.get('external-id-value')
                        # Verifica se "external-id-url" esiste e contiene un valore valido
                        url_data = ext_id.get('external-id-url')
                        if url_data is not None:
                            url = url_data.get('value')

                if doi is None:
                    continue

                # Verifica e ottieni il titolo, se esiste, altrimenti stringa vuota
                title = summary.get('title', {}).get('title', {}).get('value', "")

                # Verifica e ottieni l'anno di pubblicazione, se esiste, altrimenti stringa vuota
                publication_date = summary.get('publication-date', {})
                if publication_date:
                    year = publication_date.get('year', {}).get('value', "")
                else:
                    year = ""
                    continue

                # Verifica e ottieni il tipo di lavoro (paper_type), se esiste, altrimenti stringa vuota
                paper_type = summary.get('type', "")
                if int(year) > 2018:
                    authors = get_contributors_from_crossref(doi)
                    papers.append((doi, title, year, paper_type,  url, authors))

    return papers


def list_to_csv(papers: list) -> None:
    with open('data/raw/papers.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Doi', 'Title', 'Year', 'Type', 'Url', 'Authors'])
        for paper in papers:
            authors_str = ", ".join(paper[5])
            writer.writerow([paper[0], paper[1],  paper[2], paper[3], paper[4], authors_str])


def get_papers_metainformation_staffs(professor_df: pd.DataFrame) -> None:
    dataset = []
    for index, row in professor_df.iterrows():
        orcid = row["ORCID ID"]
        if orcid and pd.notna(orcid):
            rows = get_papers_metainformation_staff(orcid)
            if rows:
                for row in rows:
                    if row not in dataset:
                        dataset.append(row)
    list_to_csv(dataset)


if __name__ == "__main__":
    file_path = 'data/processed/professors_orcid_info2.csv'
    dataframe = pd.read_csv(file_path, sep=",")
    dataframe_subset = dataframe.iloc[51:101]
    get_papers_metainformation_staffs(dataframe)
