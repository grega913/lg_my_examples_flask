
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

from icecream import ic

# here we find the directory where we have helperz_tutorials.py
parent_dir_of_helperz_tutorials = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# we append this directory to the sys path
sys.path.append(parent_dir_of_helperz_tutorials)
# now we can import function from this file/module
from helperz_tutorials import stream_graph_updates

class State(TypedDict):
    messages: Annotated[list, add_messages]

def part2_compile_graph():

    class State(TypedDict):
        messages: Annotated[list, add_messages]


    graph_builder = StateGraph(State)


    tool = TavilySearchResults(max_results=2)
    tools = [tool]
    llm = ChatGroq()
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
    # Any time a tool is called, we return to the chatbot to decide the next step
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.set_entry_point("chatbot")
    graph = graph_builder.compile()

    return graph


'''
graph As Class
'''
class GraphPart2:
    def __init__(self):
        ic("def init")

        self.graph_builder = StateGraph(State)
        self.tool = TavilySearchResults(max_results=2)
        self.tools = [self.tool]
        self.llm = ChatGroq()
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def chatbot(self, state: State):
        ic("def chatbot")

        return {"messages": [self.llm_with_tools.invoke(state["messages"])]}


    def compile_graph(self):
        ic("def compile_graph")

        tool_node = ToolNode(tools=[self.tool])
        self.graph_builder.add_node("chatbot", self.chatbot)
        self.graph_builder.add_node("tools", tool_node)

        self.graph_builder.add_conditional_edges(
            "chatbot",
            tools_condition,
        )
        # Any time a tool is called, we return to the chatbot to decide the next step
        self.graph_builder.add_edge("tools", "chatbot")
        self.graph_builder.set_entry_point("chatbot")

        self.graph = self.graph_builder.compile()

        
    
    def stream_graph_updates(self, user_input: str):
        ic("def stream_graph_updates")

        events_count = 0
        values_count = 0

        for event in self.graph.stream({"messages": [("user", user_input)]}):
            events_count +=1
            ic(event)
            ic(events_count)
            for value in event.values():
                values_count +=1
                ic(values_count)
                ic(value)
                ic("Assistant:", value["messages"][-1].content)
                






if __name__ == "__main__":
    ic("def main")

    '''
    graph = part2_compile_graph()
    ic("we have graph")
    user_input = "Talk to me . . or better . . what do you know abot LangGraph?"
    ic(user_input)

    # stream_graph_updates(graph=graph, user_input=user_input)
    '''

    graphPart2= GraphPart2()
    graphPart2.compile_graph()

    ic(graphPart2)

    user_input = "Talk to me . . or better . . what do you know abot LangGraph?"

    graphPart2.stream_graph_updates(user_input=user_input)