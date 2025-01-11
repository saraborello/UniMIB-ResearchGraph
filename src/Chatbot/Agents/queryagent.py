from langchain_community.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
from langchain_google_genai import GoogleGenerativeAI
import os

class QueryAgent:
    def __init__(self, neo4j_uri, neo4j_username, neo4j_password, google_api_key, model="gemini-1.5-flash-latest"):
        """
        Initialize the QueryAgent.

        :param neo4j_uri: URI for the Neo4j database.
        :param neo4j_username: Username for Neo4j authentication.
        :param neo4j_password: Password for Neo4j authentication.
        :param google_api_key: API key for Google Generative AI.
        :param model: Model to use for Google Generative AI.
        """
       
        os.environ["NEO4J_URI"] = neo4j_uri
        os.environ["NEO4J_USERNAME"] = neo4j_username
        os.environ["NEO4J_PASSWORD"] = neo4j_password

        
        self.graph = Neo4jGraph()
        self.llm = GoogleGenerativeAI(model=model, google_api_key=google_api_key)

        self.chain = GraphCypherQAChain.from_llm(
            graph=self.graph,
            llm=self.llm,
            verbose=True,
            allow_dangerous_requests=True,
            validate_cypher=True
        )

    def query(self, user_input):
        """
        Execute a query based on user input and knowledge graph context.

        :param user_input: The user's query in natural language.
        :param knowledge_graph_context: Context describing the knowledge graph structure.
        :return: The response from the chain.
        """

        knowledge_graph_context = """
        You are an expert in Cypher queries for a Neo4j database.
        The database contains the following structure:
        - Author nodes (label: Author) with properties: orcid, nome, cognome, keywords, department_code, specific_field, role, organization, h_index, citations, past_institutions, internal, openalex_id_institution.
        - Paper nodes (label: Paper) with properties: doi, title, topic, subfield, field, domain, cites, cited_by, keywords, year, url.
        - Institution nodes (label: Institution) with properties: openalex_id, name, country, type, homepage_url, works_count, cited_by_count.
        - Topic nodes (label: Topic) with properties: name, field, domain.
        Relationships:
        - (Author)-[:HAS_WRITTEN]->(Paper)
        - (Author)-[:AFFILIATED_WITH]->(Institution)
        - (Paper)-[:RELATED_TO]->(Topic)

        Generate a Cypher query based on the user's input.
        
        Example:
        1. User: "Who wrote papers about Artificial Intelligence in 2021 and is affiliated with an institution in Italy?"
        Query: MATCH (a:Author)-[:HAS_WRITTEN]->(p:Paper)-[:RELATED_TO]->(t:Topic {name: 'Artificial Intelligence'})
                WHERE p.year = 2021 AND EXISTS { MATCH (a)-[:AFFILIATED_WITH]->(i:Institution {country: 'Italy'}) }
                RETURN a.nome, a.cognome, p.title, p.year, i.name

        User input: "{user_input}"
        Query:
        """


        response = self.chain.invoke({
            "query": user_input,
            "context": knowledge_graph_context
        })
        return response['result']


