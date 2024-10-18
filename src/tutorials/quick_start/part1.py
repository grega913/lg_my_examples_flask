from typing import Annotated
from langchain_groq import ChatGroq
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages

from icecream import ic


def part1_compile_graph():
    ic("def part1_compile_graph")

    class State(TypedDict):
        messages: Annotated[list, add_messages]

    graph_builder = StateGraph(State)

    llm=ChatGroq()


    def chatbot(state: State):
        return {"messages": [llm.invoke(state["messages"])]}


    # The first argument is the unique node name
    # The second argument is the function or object that will be called whenever
    # the node is used.
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.set_entry_point("chatbot")
    graph_builder.set_finish_point("chatbot")
    graph = graph_builder.compile()

    return graph

def part1_stream_graph(graph, user_input: str):

    ic(f"{user_input} in def part1_stream_graph")


    for event in graph.stream({"messages": [("user", user_input)]}):
        for value in event.values():
            content = value["messages"][-1].content
            ic(content)
            
            return content


if __name__ == "__main__":
    ic("def main")

    graph = part1_compile_graph()
    ic("we have graph")
    user_input = "Talk to me . . or better . . write a 3 sentence paragraph about why drumming is cool"
    ic(user_input)

    for event in graph.stream({"messages": [("user", user_input)]}):
        for value in event.values():
            content = value["messages"][-1].content
            ic(content)
            
    ic("end")




