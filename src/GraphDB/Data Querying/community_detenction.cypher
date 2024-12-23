/*
This query identifies authors who collaborated on the same paper 
and share the same 'internal' property value ('DISCO'). 
It then establishes CO_AUTHOR_WITH relationships between them 
to represent their co-authorship network.
*/
MATCH (a1:Author)-[:HAS_WRITTEN]->(p:Paper)<-[:HAS_WRITTEN]-(a2:Author)
WHERE a1 <> a2 AND a1.internal = "DISCO" AND a2.internal = "DISCO"
MERGE (a1)-[:CO_AUTHOR_WITH]->(a2)

/*
Louvain requires numeric node properties for computations like modularity. 
This query converts the 'internal' property into a numeric format for compatibility.
*/
MATCH (a:Author)
SET a.internal_numeric = CASE 
    WHEN a.internal = "Disco" THEN 1
    ELSE 0
END

/*
Projects a graph of 'Author' nodes with the 'internal' property and 
'CO_AUTHOR_WITH' relationships for community detection using GDS algorithms 
like Louvain. Ensure the GDS plugin is installed first.
*/
CALL gds.graph.project(
    'authorGraph',
    'Author',
    'CO_AUTHOR_WITH',
    {
        nodeProperties: ['internal_numeric']
    }
)

/*
Executes the Louvain algorithm to detect communities. 
The algorithm assigns each node a community ID, which is written 
to the 'community' property of 'Author' nodes in the graph.
*/
CALL gds.louvain.write(
    'authorGraph',
    {
        writeProperty: 'community'
    }
)

/*
Displays the community assignments for authors with internal = "DISCO". 
*/
MATCH (a:Author)
WHERE a.internal = "DISCO"
RETURN a.nome, a.cognome, a.community
ORDER BY a.community

