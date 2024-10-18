
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


def part3_compile_graph():
    ic(" - - - - - part3_compile_graph - - - - - ")
    

    class State(TypedDict):
        messages: Annotated[list, add_messages]


    graph_builder = StateGraph(State)


    tool = TavilySearchResults(max_results=2)
    tools = [tool]
    #llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
    llm= ChatGroq()
    llm_with_tools = llm.bind_tools(tools)


    def chatbot(state: State):
        return {"messages": [llm_with_tools.invoke(state["messages"])]}


    graph_builder.add_node("chatbot", chatbot)

    tool_node = ToolNode(tools=[tool])
    graph_builder.add_node("tools", tool_node)

    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
    )
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.set_entry_point("chatbot")
    graph = graph_builder.compile(checkpointer=memory)

    return graph




if __name__ == "__main__":
    ic("def main")

    graph = part3_compile_graph()
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



    

