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
// Caricamento dei dati da authors.csv
LOAD CSV WITH HEADERS FROM 'file:///authors.csv' AS author_row
WITH author_row WHERE author_row.`ORCID ID` IS NOT NULL AND author_row.`ORCID ID` <> ""
MERGE (a:Author {orcid: TRIM(author_row.`ORCID ID`)})
SET a.nome = author_row.`Given Name`,
    a.cognome = author_row.`Family Name`,
    a.keywords = split(author_row.Keywords, ", ")
WITH 1 AS dummy // Mantiene il contesto per il prossimo blocco

// Caricamento dei dati da papers.csv
LOAD CSV WITH HEADERS FROM 'file:///papers.csv' AS paper_row
WITH paper_row, split(TRIM(paper_row.Authors), ",") AS author_orcids
MERGE (p:Paper {doi: TRIM(paper_row.Doi)})
SET p.title = paper_row.Title,
    p.topic = paper_row.Topic,
    p.url = paper_row.Url
WITH p, author_orcids // Passa il contesto ai prossimi blocchi

// Creazione delle relazioni tra Paper e Author
FOREACH (orcidId IN author_orcids |
    MERGE (a:Author {orcid: TRIM(orcidId)})
    MERGE (a)-[:HAS_WRITTEN]->(p)
)

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
