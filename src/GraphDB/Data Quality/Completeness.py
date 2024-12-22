from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()


def check_data_quality(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))

    # Queries for completeness
    completeness_queries = [
        {
            "description": "Authors missing associated papers",
            "query": """
                MATCH (a:Author)
                WHERE NOT (a)-[:HAS_WRITTEN]->(:Paper)
                WITH COUNT(a) AS missing_count
                MATCH (a:Author)
                RETURN missing_count, COUNT(a) AS total_count
            """
        },
        {
            "description": "Papers missing associated topics",
            "query": """
                MATCH (p:Paper)
                WHERE NOT (p)-[:RELATED_TO]->(:Topic)
                WITH COUNT(p) AS missing_count
                MATCH (p:Paper)
                RETURN missing_count, COUNT(p) AS total_count
            """
        },
        {
            "description": "Authors missing associated institutions",
            "query": """
                MATCH (a:Author)
                WHERE NOT (a)-[:AFFILIATED_WITH]->(:Institution)
                WITH COUNT(a) AS missing_count
                MATCH (a:Author)
                RETURN missing_count, COUNT(a) AS total_count
            """
        },
        {
            "description": "Institutions missing associated authors",
            "query": """
                MATCH (i:Institution)
                WHERE NOT (i)<-[:AFFILIATED_WITH]-(:Author)
                WITH COUNT(i) AS missing_count
                MATCH (i:Institution)
                RETURN missing_count, COUNT(i) AS total_count
            """
        }
    ]

    # Query for orphan nodes
    orphan_query = """
        CALL db.labels() YIELD label
        WITH label
        CALL apoc.cypher.run(
        'MATCH (n:' + label + ') WHERE NOT (n)--() RETURN COUNT(n) AS orphan_count',
        {}
        ) YIELD value
        RETURN label AS node_type, value.orphan_count AS orphan_count
    """

    with driver.session() as session:
        # Completeness checks
        print("Running completeness checks...")
        for q in completeness_queries:
            print(f"Running: {q['description']}")
            result = session.run(q["query"])
            for record in result:
                missing_count = record["missing_count"]
                total_count = record["total_count"]
                percentage_missing = (missing_count / total_count * 100) if total_count > 0 else 0
                print(f"  Missing: {missing_count}")
                print(f"  Total: {total_count}")
                print(f"  Percentage Missing: {percentage_missing:.2f}%")

        # Orphan node check
        print("\nRunning orphan node check for all node types...")
        result = session.run(orphan_query)
        for record in result:
            node_type = record["node_type"]
            orphan_count = record["orphan_count"]
            print(f"  Node Type: {node_type}")
            print(f"  Orphan Nodes: {orphan_count}")

    # Close the connection
    driver.close()


if __name__ == "__main__":
    uri = "bolt://localhost:7687"  
    user = "neo4j"  
    password = os.getenv("DATABASE_PASSWORD")

    check_data_quality(uri, user, password)

