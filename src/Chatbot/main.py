#from langgraph.graph import StateGraph, START, END
#from langgraph.graph.message import add_messages
from Agents.queryagent import QueryAgent
from Agents.answeragent import AnswerAgent
#from src.agents.compliance_agent import ComplianceAgent
#from typing import Annotated
#from typing_extensions import TypedDict
from dotenv import load_dotenv
load_dotenv()
import os

query_agent = QueryAgent(
        neo4j_uri=os.getenv("DATABASE_URI"),
        neo4j_username=os.getenv("DATABASE_PASSWORD"),
        neo4j_password=os.getenv("DATABASE_USER"),
        google_api_key=os.getenv("GEMINI_KEY")
    )

answer_agent = AnswerAgent(api_key=os.getenv("GEMINI_KEY"))



# Define the user input
user_input = "What are the main research areas, and how many publications are associated with each area? Order in a descendant way."

# Invoke the query
response1 = query_agent.query(user_input)
response = answer_agent.run(response1)
    

# Print the response
print(response)
