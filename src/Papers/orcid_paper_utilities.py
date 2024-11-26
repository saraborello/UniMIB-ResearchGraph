import csv
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ElementTree
import pandas as pd
import requests
from dotenv import load_dotenv
load_dotenv()
from src.Authors.orcid_data_utilities import search_orcid_by_name, get_orcid_profile


def get_abstract_by_doi(doi):
    url = f"https://api.openalex.org/works/https://doi.org/{doi}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        abstract_index = data.get("abstract_inverted_index")
        if abstract_index:
            max_position = max(pos for positions in abstract_index.values() for pos in positions)
            abstract_words = [""] * (max_position + 1)
            for word, positions in abstract_index.items():
                for pos in positions:
                    abstract_words[pos] = word
            abstract_text = " ".join(abstract_words)
            return abstract_text
        else:
            return "Empty abstract"
    else:
        return "Error for the doi {doi}"


def get_contributors_from_crossref(doi: str, orcid_original: str):
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)
    author_orcids = [orcid_original]

    if response.status_code == 200:
        data = response.json()
        message = data.get("message", {})
        authors = message.get("author", [])
        for author in authors:
            orcid_link = author.get('ORCID', "")
            orcid = orcid_link[17:]
            given = author.get("given", "")
            family = author.get("family", "")

            # Log author details if incomplete
            if not given or not family:
                continue

            # Search ORCID if not available
            if not orcid:
                orcid_result = search_orcid_by_name(given, family)

                if orcid_result is None:
                    continue
                else:
                    # Safely access 'expanded-result'
                    expanded_result = orcid_result.get('expanded-result', [])
                    if not expanded_result:
                        continue
                    else:
                        # Extract ORCID ID from the first result
                        orcid = expanded_result[0].get('orcid-id', "No ORCID ID Found")

            # Avoid duplicates
            if orcid not in author_orcids:
                author_orcids.append(orcid)

        return author_orcids
    else:
        print(f"Could not retrieve authors using CrossRef for the paper with DOI {doi}")
        return None


def get_paper_details(doi):
    base_url = f"https://api.openalex.org/works/https://doi.org/{doi}"
    response = requests.get(base_url)

    if response.status_code == 200:
        try:
            data = response.json()
        except ValueError:
            print("Error: Response is not in JSON format.")
            return None

        # Extracting details with additional None checks
        if not data.get("primary_topic", {}):
            return None
        primary_location = data.get("primary_location") or {}
        source_info = primary_location.get("source") or {}

        details = {
            "title": data.get("title"),
            "publication_year": data.get("publication_year"),
            "source": source_info.get("display_name"),
            "type": data.get("type"),
            "topic": data.get("primary_topic", {}).get("display_name"),
            "subfield": data.get("primary_topic", {}).get("subfield", {}).get("display_name"),
            "field": data.get("primary_topic", {}).get("field", {}).get("display_name"),
            "domain": data.get("primary_topic", {}).get("domain", {}).get("display_name"),
            "cites": len([citation for citation in data.get("referenced_works", [])]),
            "cited_by": data.get("cited_by_count"),
            "keywords": [kw.get("display_name") for kw in data.get("keywords", []) if kw]
        }
        return details
    else:
        print(f"Error: Unable to fetch data. Status code {response.status_code}, with doi {doi}")
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
                    abstract = get_abstract_by_doi(doi)
                    papers.append((doi, title, year, paper_type,  url, authors, topic,
                                   subfield, field, domain, cites, cited_by,
                                   keywords, abstract))

    return papers


def list_to_csv(papers: list) -> None:
    with open('data/raw/papers5.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Doi', 'Title', 'Year', 'Type', 'Url', 'Authors',
                         'Topic', 'Subfield', 'Field', 'Domain', 'Cites',
                         'Cited_by', 'Keywords', 'Abstract'])
        for paper in papers:
            authors_str = ", ".join(paper[5])
            writer.writerow([paper[0], paper[1],  paper[2], paper[3], paper[4], authors_str,
                             paper[6], paper[7], paper[8], paper[9],
                             paper[10],paper[11],paper[12]])


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
    dataframe_subset = dataframe.iloc[76:]
    get_papers_metainformation_staffs(dataframe_subset)
