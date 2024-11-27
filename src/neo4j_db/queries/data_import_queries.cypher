
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

#refactor garph
MATCH (p:Paper {doi: '10.1038/s41467-019-09799-2'})
DETACH DELETE p;
MATCH (a:Author)
WHERE NOT (a)-[:HAS_WRITTEN]->(:Paper)
DETACH DELETE a;
MATCH (i:Institution)
WHERE NOT (i)<-[:AFFILIATED_WITH]-(:Author)
DETACH DELETE i;

