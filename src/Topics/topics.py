import pandas as pd
from dotenv import load_dotenv
load_dotenv()

import csv


def get_topics(data) -> list:

    topic_dict = {}

    for index, row in data.iterrows():
        topic = row["Topic"]
        subfield = row["Subfield"]
        field = row["Field"]
        domain = row["Domain"]
        if topic not in topic_dict:
            topic_dict[topic] = [field, subfield, domain]

    return list(topic_dict.items())


def list_to_csv(topic_list):
    with open('data/processed/topic.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Topic', 'Field', 'Subfield', 'Domain'])
        for topic in topic_list:
            writer.writerow([topic[0], topic[1][0],  topic[1][1], topic[1][2]])


if __name__ == "__main__":
    df = pd.read_csv("data/processed/papers.csv", sep=",")
    topics = get_topics(df)
    list_to_csv(topics)
