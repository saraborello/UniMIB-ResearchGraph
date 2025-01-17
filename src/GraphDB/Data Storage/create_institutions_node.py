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
// Caricamento dei dati e creazione dei nodi Institution, poi collegamento con gli autori
LOAD CSV WITH HEADERS FROM 'file:///Institutions.csv' AS institution_row
WITH institution_row
WHERE TRIM(institution_row.openalex_id) IS NOT NULL AND TRIM(institution_row.openalex_id) <> ""
MERGE (i:Institution {openalex_id: TRIM(institution_row.openalex_id)})
SET i.name = institution_row.corrected_university_name,
    i.country = institution_row.country,
    i.type = institution_row.type,
    i.homepage_url = institution_row.homepage_url,
    i.works_count = toInteger(institution_row.works_count), // Conversione in intero
    i.cited_by_count = toInteger(institution_row.cited_by_count) // Conversione in intero
WITH i
// Aggiungi gli autori e collega utilizzando openalex_id
MATCH (a:Author) // Seleziona gli autori già esistenti nel grafo
WHERE a.openalex_id_institution IS NOT NULL AND a.openalex_id_institution <> ""
MATCH (inst:Institution {openalex_id: a.openalex_id_institution}) // Verifica che l'istituzione esista
MERGE (a)-[:AFFILIATED_WITH]->(inst) // Crea la relazione solo se l'istituzione esiste


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