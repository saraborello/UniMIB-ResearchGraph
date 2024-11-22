from neo4j import GraphDatabase

# Configurazione del database
NEO4J_URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "elicottero"

class Neo4jConnector:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def execute_query(self, query):
        with self.driver.session() as session:
            result = session.run(query)
            return result

# Nuova Query Cypher
query = """
// Caricamento dei dati da InstitutionsFinale.csv e creazione dei nodi Institution
LOAD CSV WITH HEADERS FROM 'file:///Institutions.csv' AS institution_row
FIELDTERMINATOR ';'
WITH institution_row
WHERE TRIM(institution_row.openalex_id) IS NOT NULL AND TRIM(institution_row.openalex_id) <> ""
MERGE (i:Institution {openalex_id: TRIM(institution_row.openalex_id)})
SET i.name = institution_row.Institution,
    i.country = institution_row.country,
    i.type = institution_row.type,
    i.homepage_url = institution_row.homepage_url,
    i.works_count = toInteger(institution_row.works_count), // Conversione in intero
    i.cited_by_count = toInteger(institution_row.cited_by_count) // Conversione in intero
WITH i

MATCH (a:Author) // Seleziona gli autori già esistenti nel grafo
WHERE a.organization IS NOT NULL
MERGE (inst:Institution {name: a.organization}) // Crea o collega al nodo Institution
MERGE (a)-[:AFFILIATED_WITH]->(inst)

"""

if __name__ == "__main__":
    connector = Neo4jConnector(NEO4J_URI, USERNAME, PASSWORD)
    try:
        connector.execute_query(query)
        print("Query eseguita con successo!")
    except Exception as e:
        print(f"Errore durante l'esecuzione della query: {e}")
    finally:
        connector.close()