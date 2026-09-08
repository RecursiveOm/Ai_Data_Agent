from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()


def pick_llm(level: str):
    """
    Picks the appropriate DeepSeek LLM based on the level of the question.
    """

    if level.lower() == "low":
        llm = ChatOpenAI(
            model="deepseek-chat",
            temperature=0,
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )

    elif level.lower() == "medium":
        llm = ChatOpenAI(
            model="deepseek-reasoner",
            temperature=0,
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )

    elif level.lower() == "high":
        llm = ChatOpenAI(
            model="deepseek-reasoner",
            temperature=0,
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )

    else:
        raise ValueError(f"Unsupported level: {level}")

    return llm


if __name__ == "__main__":
    llm_obj = pick_llm("low")

    response = llm_obj.invoke(
        "What is the capital of France?"
    )

    print(response.content)