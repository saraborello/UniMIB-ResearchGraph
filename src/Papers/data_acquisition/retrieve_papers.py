import csv
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ElementTree
import pandas as pd
import requests
import time
from dotenv import load_dotenv
load_dotenv()
from src.Authors.data_acquisition.orcid_data_utilities import search_orcid_by_name, get_orcid_profile


def get_contributors_from_crossref(doi: str, orcid_original: str):
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)
    author_orcids = [orcid_original]

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 429:  # Too Many Requests
            retry_after = int(response.headers.get("Retry-After", 1))
            print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
            return get_contributors_from_crossref(doi, orcid_original)  # Retry

        response.raise_for_status()
        data = response.json()
        message = data.get("message", {})
        authors = message.get("author", [])

        for author in authors:
            orcid_link = author.get("ORCID", "")
            orcid = orcid_link[17:] if orcid_link.startswith("https://orcid.org/") else ""

            given = author.get("given", "")
            family = author.get("family", "")

            if not given or not family:
                continue

            if not orcid:
                orcid_result = search_orcid_by_name(given, family)
                if orcid_result:
                    expanded_result = orcid_result.get("expanded-result", [])
                    if expanded_result:
                        orcid = expanded_result[0].get("orcid-id", "")

            if orcid and orcid not in author_orcids:
                author_orcids.append(orcid)

        return author_orcids

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error: {http_err}. DOI: {doi}")
    except requests.exceptions.Timeout:
        print(f"Timeout error. DOI: {doi}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error: {req_err}. DOI: {doi}")

    return None



def get_paper_details(doi):
    base_url = f"https://api.openalex.org/works/https://doi.org/{doi}"
    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        try:
            data = response.json()
        except ValueError:
            print("Errore: La risposta non è in formato JSON.")
            return None

        # Extract relevant details
        primary_location = data.get("primary_location", {})
        details = None
        if data.get("primary_topic", {}) and data:
            details = {
                "title": data.get("title"),
                "publication_year": data.get("publication_year"),
                "type": data.get("type"),
                "topic": data.get("primary_topic", {}).get("display_name"),
                "subfield": data.get("primary_topic", {}).get("subfield", {}).get("display_name"),
                "field": data.get("primary_topic", {}).get("field", {}).get("display_name"),
                "domain": data.get("primary_topic", {}).get("domain", {}).get("display_name"),
                "cites": len(data.get("referenced_works", [])),
                "cited_by": data.get("cited_by_count"),
                "keywords": [kw.get("display_name") for kw in data.get("keywords", []) if kw],
            }
        return details

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error: {http_err}. DOI: {doi}")
    except requests.exceptions.Timeout:
        print(f"Timeout error. DOI: {doi}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error: {req_err}. DOI: {doi}")

    return None

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
                        url_data = ext_id.get('external-id-url')
                        if url_data is not None:
                            url = url_data.get('value')

                if doi is None:
                    continue

                details = get_paper_details(doi)
                if details is None:
                    continue
                year = details["publication_year"]

                if int(year) > 2018:
                    title = details["title"]
                    paper_type = summary.get('type', "")
                    topic = details["topic"]
                    subfield = details["subfield"]
                    field = details["field"]
                    domain = details["domain"]
                    cites = details["cites"]
                    cited_by = details["cited_by"]
                    keywords = details["keywords"]
                    authors = get_contributors_from_crossref(doi, orcid)
                    if not authors:
                        continue
                    papers.append((doi, title, year, paper_type,  url, authors, topic,
                                   subfield, field, domain, cites, cited_by,
                                   keywords))

    return papers


def list_to_csv(papers: list) -> None:
    with open('data/raw/papers_duplicated.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Doi', 'Title', 'Year', 'Type', 'Url', 'Authors',
                         'Topic', 'Subfield', 'Field', 'Domain', 'Cites',
                         'Cited_by', 'Keywords'])
        for paper in papers:
            authors_str = ", ".join(paper[5])
            writer.writerow([paper[0], paper[1],  paper[2], paper[3], paper[4], authors_str,
                             paper[6], paper[7], paper[8], paper[9],
                             paper[10],paper[11]])


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
    file_path = 'data/raw/Authors_internal.csv'
    dataframe = pd.read_csv(file_path, sep=",")
    dataframe_subset = dataframe.iloc[:3]
    get_papers_metainformation_staffs(dataframe)
