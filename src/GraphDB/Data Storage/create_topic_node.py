

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
// Caricamento dei dati dei Topic da un file CSV e creazione dei nodi Topic
LOAD CSV WITH HEADERS FROM 'file:///topic.csv' AS topic_row
WITH topic_row
MERGE (t:Topic {name: TRIM(topic_row.Subfield)}) // Nodo Topic basato sulla chiave 'Subfield'
SET t.field = topic_row.Field,                 // Imposta il campo 'Field'
    t.domain = topic_row.Domain                // Imposta il campo 'Domain'

// Collegamento dei Paper ai relativi Topic
WITH t
MATCH (p:Paper)                                // Trova i nodi Paper esistenti
WHERE p.subfield = t.name                      // Collega solo i Paper con lo stesso Subfield
MERGE (p)-[:RELATED_TO]->(t)                   // Crea la relazione
;


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
