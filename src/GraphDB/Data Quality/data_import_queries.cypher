#refactor garph
MATCH (p:Paper {doi: '10.1038/s41467-019-09799-2'})
DETACH DELETE p;
MATCH (a:Author)
WHERE NOT (a)-[:HAS_WRITTEN]->(:Paper)
DETACH DELETE a;
MATCH (i:Institution)
WHERE NOT (i)<-[:AFFILIATED_WITH]-(:Author)
DETACH DELETE i;

