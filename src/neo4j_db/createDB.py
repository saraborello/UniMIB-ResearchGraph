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
// Caricamento dei dati da Authors_internal.csv
LOAD CSV WITH HEADERS FROM 'file:///Authors.csv' AS author_row
FIELDTERMINATOR ';'
WITH author_row 
WHERE TRIM(author_row.`ORCID ID`) IS NOT NULL AND TRIM(author_row.`ORCID ID`) <> ""
MERGE (a:Author {orcid: TRIM(author_row.`ORCID ID`)})
SET a.nome = author_row.`Given Name`,
    a.cognome = author_row.`Family Name`,
    a.keywords = split(author_row.Keywords, ", "),
    a.department_code = author_row.`Department Code`,
    a.specific_field = author_row.`Specific Field`,
    a.role = author_row.Role,
    a.organization = author_row.Organization,
    a.h_index = toInteger(author_row.`H Index`),
    a.citations = toInteger(author_row.Citations),
    a.past_institutions = split(author_row.`Past Institutions`, ", "),
    a.internal = author_row.Internal
WITH 1 AS dummy // Mantieni il contesto per passare al blocco successivo

// Caricamento dei dati da papers.csv e creazione delle relazioni
LOAD CSV WITH HEADERS FROM 'file:///papers.csv' AS paper_row
WITH paper_row, 
     [orcid IN split(paper_row.Authors, ",") | TRIM(orcid)] AS author_orcids
WHERE TRIM(paper_row.Doi) IS NOT NULL AND TRIM(paper_row.Doi) <> ""
MERGE (p:Paper {doi: TRIM(paper_row.Doi)})
SET p.title = paper_row.Title,
    p.topic = paper_row.Topic,
    p.subfield = paper_row.Subfield,
    p.field = paper_row.Field,
    p.domain = paper_row.Domain,
    p.cites = toInteger(paper_row.Cites),
    p.cited_by = toInteger(paper_row.Cited_by),
    p.keywords = split(paper_row.Keywords, ", "),
    p.year = toInteger(paper_row.Year),
    p.url = paper_row.Url
WITH p, author_orcids
UNWIND author_orcids AS orcidId
MATCH (a:Author {orcid: orcidId}) // Connettiti solo agli autori esistenti
MERGE (a)-[:HAS_WRITTEN]->(p)


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
