import os
import sys
import json

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from utils.llm_pick import pick_llm
from Models.schema import DataAgentSchema
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START
from agents.etl_analyst import etl_analyst
from agents.sql_analyst import sql_analyst


# ---------------------------- LLM ---------------------------- #

llm = pick_llm("medium")


# ---------------------------- ROUTER ---------------------------- #

def router_node(state: DataAgentSchema):

    message = state.messages[-1].content

    router_prompt = f"""
You are a routing agent for a data analysis system.

Your job is to decide which agent should handle the user's request.

Available agents:

1. sql
   Use this when the user wants:
   - Database queries
   - SQL operations
   - Data already stored in PostgreSQL
   - Tables, rows, columns
   - Database analysis

2. etl
   Use this when the user wants:
   - Extract data from an API
   - Extract data from a file
   - Transform data
   - Save data to CSV
   - Load data into a database
   - ETL pipelines

Return ONLY one word:

sql

OR

etl

Do not explain your answer.

User request:
{message}
"""

    response = llm.invoke(router_prompt)

    route_response = response.content.strip().lower()

    # Handle cases where the model returns extra text
    if "etl" in route_response:
        route_response = "etl"

    elif "sql" in route_response:
        route_response = "sql"

    else:
        raise ValueError(
            f"Invalid route response from LLM: {response.content}"
        )

    state.route_response = route_response

    return state


# ---------------------------- ETL NODE ---------------------------- #

def etl_node(state: DataAgentSchema):

    message = state.messages[-1].content

    response = etl_analyst.invoke(
        {
            "messages": [
                HumanMessage(
                    content=message
                )
            ]
        }
    )

    state.messages = state.messages + [response]

    return state


# ---------------------------- SQL NODE ---------------------------- #

def sql_node(state: DataAgentSchema):

    message = state.messages[-1].content

    input_schema = {
        "messages": [],
        "user_question": message,
        "curated_ques": "",
        "prompt_query_context": "",
        "generated_sql_query": "",
        "is_safe": "No",
        "comments": "",
        "sql_query_execution_result": "",
        "final_answer": ""
    }

    response = sql_analyst.invoke(input_schema)

    state.messages = state.messages + [response]

    return state


# ---------------------------- GRAPH ---------------------------- #

data_agent_graph = StateGraph(DataAgentSchema)

data_agent_graph.add_node(
    "router_node",
    router_node
)

data_agent_graph.add_node(
    "etl_node",
    etl_node
)

data_agent_graph.add_node(
    "sql_node",
    sql_node
)


# START → Router

data_agent_graph.add_edge(
    START,
    "router_node"
)


# ---------------------------- CONDITIONAL ROUTING ---------------------------- #

def route_edge(state: DataAgentSchema) -> str:

    if state.route_response == "sql":
        return "sql_node"

    elif state.route_response == "etl":
        return "etl_node"

    else:
        raise ValueError(
            f"Invalid route response: {state.route_response}"
        )


data_agent_graph.add_conditional_edges(
    "router_node",
    route_edge,
    {
        "sql_node": "sql_node",
        "etl_node": "etl_node"
    }
)


# Compile graph

data_agent = data_agent_graph.compile()


# ---------------------------- SAVE GRAPH IMAGE ---------------------------- #

try:

    from IPython.display import Image

    img = Image(
        data_agent.get_graph().draw_mermaid_png()
    )

    with open(
        "data_agent_graph.png",
        "wb"
    ) as f:

        f.write(img.data)

except Exception as e:

    print(
        f"Could not save graph image: {e}"
    )


# ---------------------------- TEST ---------------------------- #

if __name__ == "__main__":

    user_request = """
    I want to extract the data from the API endpoint
    'https://pokeapi.co/api/v2/pokemon'
    and save it to the data/extract folder in the csv folder.
    """

    response = data_agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content=user_request
                )
            ],
            "route_response": ""
        }
    )

    print("\n---------------- RESULT ----------------\n")

    print(response)

