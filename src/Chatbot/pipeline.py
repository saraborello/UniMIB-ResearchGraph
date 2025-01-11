from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from Agents.queryagent import QueryAgent
from Agents.answeragent import AnswerAgent
from typing import Annotated
from typing_extensions import TypedDict
import os

from dotenv import load_dotenv
load_dotenv()


class ChatbotState(TypedDict):
    # State keys:
    # - `messages` to store conversation history.
    # - `documents` to store retrieved documents.
    # - `response` to store the final response.
    messages: Annotated[list, add_messages]
    documents: list
    response: str


query_agent = QueryAgent(
    neo4j_uri=os.getenv("DATABASE_URI"),
    neo4j_username=os.getenv("DATABASE_USER"),
    neo4j_password=os.getenv("DATABASE_PASSWORD"),
    google_api_key=os.getenv("GEMINI_KEY")
)

answer_agent = AnswerAgent(api_key=os.getenv("GEMINI_KEY"))


graph_builder = StateGraph(ChatbotState)


def query_graphdb(state: ChatbotState):
    """
    Retrieve documents using QueryAgent.
    """
    user_message = state["messages"][-1]  
    response1 = query_agent.query(user_message)
    return {"documents": response1}
graph_builder.add_node("query_graphdb", query_graphdb)


def generate_response(state: ChatbotState):
    """
    Generate a response using ComplianceAgent.
    """
    documents = state.get("documents", [])
    if not documents:
        return {"response": "No relevant documents found."}
    response = answer_agent.run(documents)
    return {"response": response}
graph_builder.add_node("generate_response", generate_response)

graph_builder.add_edge(START, "query_graphdb")
graph_builder.add_edge("query_graphdb", "generate_response")
graph_builder.add_edge("generate_response", END)
graph = graph_builder.compile()


def stream_graph_updates(user_input: str):
    """
    Run the graph for the given user input.
    """
    
    state = {"messages": [{"role": "user", "content": user_input}]}
    for event in graph.stream(state):
        for value in event.values():
            if "response" in value:
                print("Assistant:", value["response"])
                return


def main():
    print("Welcome to the Departmental Research Explorer!! Type 'exit' to quit.")
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            stream_graph_updates(user_input)
            continue_chat = input("Do you want to ask another question? (yes/no): ").strip().lower()
            if continue_chat not in ["yes", "y"]:
                print("Goodbye!")
                break

        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    main()
