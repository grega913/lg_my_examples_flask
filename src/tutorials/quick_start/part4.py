
import os
import sys
import pathlib
import time

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



class GraphPart4():
    def __init__(self, threadId:str):
        ic("GraphPart4 - init")
        self.memory = MemorySaver()
        self.config = {"configurable": {"thread_id": threadId}}


    def compile_graph_with_interrupt_before(self):
        ic("GraphPart4 - compile_graph_with_interrupt_before")

        class State(TypedDict):
            messages: Annotated[list, add_messages]

        graph_builder = StateGraph(State)

        tool = TavilySearchResults(max_results=2)
        tools = [tool]

        llm = ChatGroq()
        llm_with_tools = llm.bind_tools(tools)

        def chatbot(state: State):
            ic("def chatbot")
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


        # we are compiling graph with interrupt_before param
        self.graph = graph_builder.compile(checkpointer=self.memory, interrupt_before=["tools"])


    def getStream(self, user_input:str):
        ic(f"def getStream, self.config is ${self.config}")
        events = self.graph.stream({"messages": [("user", user_input)]}, self.config, stream_mode="values")
        return events
    
    # Passing in None will just let the graph continue where it left off, without adding anything new to the state
    def getStreamWithNone(self):
        ic(f"def getStreamWithNone")
        events = self.graph.stream(None, self.config, stream_mode="values")
        return events
    
    def getSnapshot(self):
        ic("def getSnapshot")
        return self.graph.get_state(self.config)


if __name__ == "__main__":
    ic("def main")

    '''
    user_input = "Hi there! My name is Marko Kovač."
    config = {"configurable": {"thread_id": "1"}}
    '''

    graphPart4 = GraphPart4(threadId="1")
    graphPart4.compile_graph_with_interrupt_before()

    user_input = "I'm learning LangGraph. Could you do some research on it for me?"
    config = {"configurable": {"thread_id": "1"}}
    # The config is the **second positional argument** to stream() or invoke()!
    events_generator = graphPart4.getStream(user_input=user_input)
    for event in events_generator:
        if "messages" in event:
            event["messages"][-1].pretty_print()
    
    snapshot = graphPart4.getSnapshot()
    ic(snapshot)
    ic(snapshot.next)
    
    existing_message = snapshot.values["messages"][-1]
    ic(existing_message)
    ic(existing_message.tool_calls)

    ic(" waiting ")
    time.sleep(5)
    ic(" after waiting ")

    events = graphPart4.getStreamWithNone()
    for event in events:
        if "messages" in event:
            event["messages"][-1].pretty_print()





    

