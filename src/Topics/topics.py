import pandas as pd
from dotenv import load_dotenv
load_dotenv()

import csv


def get_topics(data) -> list:

    topic_dict = {}

    for index, row in data.iterrows():
        subfield = row["Subfield"]
        field = row["Field"]
        domain = row["Domain"]
        if subfield not in topic_dict:
            topic_dict[subfield] = [field, domain]

    return list(topic_dict.items())


def list_to_csv(topic_list) -> None:
    with open('data/processed/topic.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Subfield', 'Field', 'Domain'])
        for topic in topic_list:
            writer.writerow([topic[0], topic[1][0],  topic[1][1]])


if __name__ == "__main__":
    df = pd.read_csv("data/processed/papers.csv", sep=",")
    topics = get_topics(df)
    list_to_csv(topics)
