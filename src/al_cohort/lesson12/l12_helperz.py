from langgraph.graph import StateGraph, START, END, MessagesState
from typing import Literal
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, RemoveMessage
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()

# define our tools
def multiply(a: float, b: float) -> float:
    """
    Multiply two numbers.

    Args:
        a: int
        b: int
    """
    return a * b

def sum(a: float, b: float) -> float:
    """
    Sum two numbers.

    Args:
        a: int
        b: int
    """
    return a + b


# initialitze the state - for that we will add a key "summary"
class State(MessagesState):
    summary: str

# define 2 nodes: chat and summarize_conversation
def chat(state: State):
    summary = state.get("summary", "")
    if summary:
        system_prompt = f"Here is the summary of the conversation earlier: {summary}"
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
    else:
        messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

# 8:53
def summarize_conversation(state: State):
    summary = state.get("summary", "")
    if summary:
        summary_prompt = f"""
        This is the summary of the conversation up to this point: {summary}. \n\n
        Extend the summary by taking into account the latest messages above.
        """
    else:
        summary_prompt = "Create a summary of the conversation up to this point."

    messages = state["messages"] + [HumanMessage(content=summary_prompt)]
    response = llm.invoke(messages)

    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response.content, "messages": delete_messages}

# 13:21
# conditional edge that sends to summary only of more than 6 messages
# basically creating our own tool_condition router
def should_summarize(state: State) -> Literal["summarize_conversation", "__end__"]:
    """
    Check if we should summarize the conversation.
    """
    messages = state["messages"]

    if len(state["messages"]) > 5:
        return "summarize_conversation"
    else:
        return "__end__"