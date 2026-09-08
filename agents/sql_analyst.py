import os 
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from utils.llm_pick import pick_llm
from Models.schema import AgentSchema


#  ------------------Ai Agent Code-----------------------


def curate_ques(state: AgentSchema) -> AgentSchema: 

    user_question = state.user_question # Bcz this is a Pydantic model object

    llm = pick_llm("low")  # Pick the appropriate LLM based on the level of the question

    response = llm.invoke(f"Curate the following question: {user_question}").content

    state.curated_ques = response
    state.messages = state.messages + [HumanMessage(content=f"{response}")]  # Append the curated question to the messages list

    return state 
