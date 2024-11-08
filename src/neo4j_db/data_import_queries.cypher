
LOAD CSV WITH HEADERS FROM 'file:///authors.csv' AS row
MERGE (a:Author {orcid: row.orcid})
SET a.nome = row.nome, a.cognome = row.cognome, a.keywords = split(row.keywords, ", ")

LOAD CSV WITH HEADERS FROM 'file:///papers.csv' AS row
MERGE (p:Paper {doi: row.doi})
SET p.topic = row.topic

FOREACH (orcidId IN split(row.orcids, ",") |
    MERGE (a:Author {orcid: orcidId})
    MERGE (a)-[:HAS_WRITTEN]->(p)
)
