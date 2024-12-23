from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

def get_top_topics(session):
    query = """
    MATCH (t:Topic)<-[:RELATED_TO]-(p:Paper)
    RETURN t.name AS TopicName, COUNT(p) AS PaperCount
    ORDER BY PaperCount DESC
    LIMIT 10
    """
    results = session.run(query)
    return [{"TopicName": record["TopicName"], "PaperCount": record["PaperCount"]} for record in results]

def get_top_collaborations(session):
    query = """
    MATCH (internalAuthor:Author)-[:HAS_WRITTEN]->(p:Paper)<-[:HAS_WRITTEN]-(externalAuthor:Author)-[:AFFILIATED_WITH]->(extInstitution:Institution)
    WHERE internalAuthor.department_code IS NOT NULL
    AND (externalAuthor.department_code IS NULL OR externalAuthor.department_code <> internalAuthor.department_code)
    RETURN extInstitution.country AS InstitutionCountry,
           extInstitution.homepage_url AS InstitutionWebsite,
           COUNT(DISTINCT p) AS CollaborationCount
    ORDER BY CollaborationCount DESC
    LIMIT 10
    """
    results = session.run(query)
    return [
        {
            "InstitutionCountry": record["InstitutionCountry"],
            "InstitutionWebsite": record["InstitutionWebsite"],
            "CollaborationCount": record["CollaborationCount"]
        }
        for record in results
    ]

def get_us_collaborations(session):
    query = """
    MATCH (prof:Author)-[:HAS_WRITTEN]->(p:Paper)<-[:HAS_WRITTEN]-(usAuthor:Author)-[:AFFILIATED_WITH]->(usInstitution:Institution),
          (p)-[:RELATED_TO]->(t:Topic)
    WHERE prof.role CONTAINS "Professor"
    AND prof.department_code IS NOT NULL
    AND usInstitution.country = "US"
    RETURN DISTINCT
           prof.nome + " " + prof.cognome AS ProfessorName,
           usAuthor.nome + " " + usAuthor.cognome AS CollaboratingAuthor,
           usInstitution.homepage_url AS InstitutionWebsite,
           COLLECT(DISTINCT t.name) AS Topics
    ORDER BY ProfessorName
    """
    results = session.run(query)
    return [
        {
            "ProfessorName": record["ProfessorName"],
            "CollaboratingAuthor": record["CollaboratingAuthor"],
            "InstitutionWebsite": record["InstitutionWebsite"],
            "Topics": record["Topics"]
        }
        for record in results
    ]

if __name__ == "__main__":
    uri = "bolt://localhost:7687"  # Update with your Neo4j URI
    user = "neo4j"  # Update with your username
    password = os.getenv("DATABASE_PASSWORD")  # Update with your password

    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session() as session:
        print("Top Topics:")
        for topic in get_top_topics(session):
            print(topic)

        print("\nTop Collaborations:")
        for collab in get_top_collaborations(session):
            print(collab)

        print("\nUS Collaborations:")
        for us_collab in get_us_collaborations(session):
            print(us_collab)

    driver.close()
