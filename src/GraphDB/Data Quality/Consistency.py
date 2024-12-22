from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

def check_duplicates(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    results_summary = []
    node_labels_query = "CALL db.labels() YIELD label RETURN label"

    relationship_types_query = "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType"

    def find_duplicate_nodes(label):
        """
        Query to find duplicate nodes for a given label.
        """
        query = f"""
        MATCH (n:{label})
        WITH n, COUNT(*) AS count
        WHERE count > 1
        RETURN COUNT(n) AS duplicate_count
        """
        with driver.session() as session:
            result = session.run(query)
            return result.single()["duplicate_count"]

    def find_duplicate_relationships(rel_type):
        """
        Query to find duplicate relationships for a given type.
        """
        query = f"""
        MATCH (a)-[r:{rel_type}]->(b)
        WITH a, b, TYPE(r) AS rel_type, COUNT(*) AS rel_count
        WHERE rel_count > 1
        RETURN COUNT(*) AS duplicate_count
        """
        with driver.session() as session:
            result = session.run(query)
            return result.single()["duplicate_count"]

    try:
        with driver.session() as session:
            print("Checking for duplicate nodes...")
            node_labels = [record["label"] for record in session.run(node_labels_query)]
            for label in node_labels:
                duplicate_count = find_duplicate_nodes(label)
                results_summary.append({
                    "type": "Node",
                    "label_or_type": label,
                    "duplicate_count": duplicate_count
                })

            print("Checking for duplicate relationships...")
            relationship_types = [record["relationshipType"] for record in session.run(relationship_types_query)]
            for rel_type in relationship_types:
                duplicate_count = find_duplicate_relationships(rel_type)
                results_summary.append({
                    "type": "Relationship",
                    "label_or_type": rel_type,
                    "duplicate_count": duplicate_count
                })

        print("\nDuplicate Summary:")
        for result in results_summary:
            print(f"{result['type']}: {result['label_or_type']}, Duplicate Count: {result['duplicate_count']}")

    finally:
        driver.close()

if __name__ == "__main__":
    uri = "bolt://localhost:7687"  
    user = "neo4j" 
    password = os.getenv("DATABASE_PASSWORD") 

    if not password:
        raise ValueError("Database password not found. Please set it in the .env file.")

    check_duplicates(uri, user, password)


    
