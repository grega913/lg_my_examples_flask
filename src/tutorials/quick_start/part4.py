
import os
import sys
import pathlib

from typing import Annotated
from langchain_groq import ChatGroq
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.checkpoint.memory import MemorySaver
from icecream import ic

# here we find the directory where we have helperz_tutorials.py
parent_dir_of_helperz_tutorials = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# we append this directory to the sys path
sys.path.append(parent_dir_of_helperz_tutorials)
# now we can import function from this file/module
from helperz_tutorials import stream_graph_updates


memory = MemorySaver()


def part4_compile_graph():
    ic(" def part4_compile_graph")

    # define State
    class State(TypedDict):
        messages: Annotated[list, add_messages]

    # define Graph
    graph_builder = StateGraph(State)


    #define tools
    tool = TavilySearchResults(max_results=2)
    tools = [tool]

    # define llm
    llm = ChatGroq()

    # bind tools to llm
    llm_with_tools = llm.bind_tools(tools)


    # define chatbot node
    def chatbot(state: State):
        return {"messages": [llm_with_tools.invoke(state["messages"])]}


    # add node to a graph
    graph_builder.add_node("chatbot", chatbot)

    # define tool node
    tool_node = ToolNode(tools=[tool])

    # add tool node to a graph
    graph_builder.add_node("tools", tool_node)

    # add conditional edge to a graph
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
    )

    # add edge to a builder
    graph_builder.add_edge("tools", "chatbot")

    # set entry point
    graph_builder.set_entry_point("chatbot")

    # define memorySaver - runtime memory here
    memory = MemorySaver()

    # compile graph with interrupt_before
    graph = graph_builder.compile(
        checkpointer=memory,
        # This is new!
        interrupt_before=["tools"],
        # Note: can also interrupt __after__ actions, if desired.
        # interrupt_after=["tools"]
    )

    return graph



if __name__ == "__main__":
    ic("def main")

    graph = part4_compile_graph()
    ic("we have graph")
    user_input = "Hi there! My name is Marko Kovač."
    config = {"configurable": {"thread_id": "1"}}




    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            events = graph.stream(
                {"messages": [("user", user_input)]}, config, stream_mode="values"
            )
            for event in events:
                ic(event["messages"][-1])
        except:
            user_input = "What do you know about LangGraph?"
            break



    

