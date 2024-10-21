
import os
import sys
import pathlib
import time

from typing import Annotated
from langchain_groq import ChatGroq
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, ToolMessage
from pydantic import BaseModel

from icecream import ic



def create_response(response: str, ai_message: AIMessage):
    ic("def create_response")
    ic(ai_message.tool_calls[0]["id"])

    return ToolMessage(
        content=response,
        tool_call_id=ai_message.tool_calls[0]["id"],
    )



class GraphPart6:

    def __init__(self):
        ic("initializing GraphPart6")
        memory = MemorySaver()
        
        class State(TypedDict):
            messages: Annotated[list, add_messages]
            # This flag is new
            ask_human: bool


        class RequestAssistance(BaseModel):
            """Escalate the conversation to an expert. 
            Use this if you are unable to assist directly or if the user requires support beyond your permissions.
            To use this function, relay the user's 'request' so the expert can provide the right guidance.
            """
            request: str


        tool = TavilySearchResults(max_results=2)
        tools = [tool]
        llm = ChatGroq()
        # We can bind the llm to a tool definition, a pydantic model, or a json schema
        llm_with_tools = llm.bind_tools(tools + [RequestAssistance])


        def chatbot(state: State):
            response = llm_with_tools.invoke(state["messages"])
            ask_human = False
            if (
                response.tool_calls
                and response.tool_calls[0]["name"] == RequestAssistance.__name__
            ):
                ask_human = True
            return {"messages": [response], "ask_human": ask_human}


        self.graph_builder = StateGraph(State)

        self.graph_builder.add_node("chatbot", chatbot)
        self.graph_builder.add_node("tools", ToolNode(tools=[tool]))

        '''
        def create_response(response: str, ai_message: AIMessage):
            ic("def create_response")
            ic(ai_message.tool_calls[0]["id"])

            return ToolMessage(
                content=response,
                tool_call_id=ai_message.tool_calls[0]["id"],
            )
        '''

        def human_node(state: State):
            new_messages = []
            if not isinstance(state["messages"][-1], ToolMessage):
                # Typically, the user will have updated the state during the interrupt.
                # If they choose not to, we will include a placeholder ToolMessage to
                # let the LLM continue.
                new_messages.append(
                    create_response("No response from human.", state["messages"][-1])
                )
            return {
                # Append the new messages
                "messages": new_messages,
                # Unset the flag
                "ask_human": False,
            }


        self.graph_builder.add_node("human", human_node)


        def select_next_node(state: State):
            if state["ask_human"]:
                return "human"
            # Otherwise, we can route as before
            return tools_condition(state)


        self.graph_builder.add_conditional_edges(
            "chatbot",
            select_next_node,
            {"human": "human", "tools": "tools", "__end__": "__end__"},
        )
        self.graph_builder.add_edge("tools", "chatbot")
        self.graph_builder.add_edge("human", "chatbot")
        self.graph_builder.set_entry_point("chatbot")

        

        self.graph = self.graph_builder.compile(
            checkpointer=memory,
            interrupt_before=["human"],
        )
















    


if __name__=="__main__":
    ic("def main")

    graphPart6 = GraphPart6()
    graph=graphPart6.graph

    user_input = "I need some expert guidance for building this AI agent. Could you request assistance for me?"
    config = {"configurable": {"thread_id": "1"}}
    # The config is the **second positional argument** to stream() or invoke()!
    events = graph.stream(
        {"messages": [("user", user_input)]}, config, stream_mode="values"
    )
    for event in events:
        if "messages" in event:
            ic(event["messages"][-1])
    
    snapshot = graph.get_state(config=config)
    ic(snapshot.next[0])


    ic(" - - - - - - - - - - - - - - Before Human Response - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ")
    time.sleep(3)

    ai_message = snapshot.values["messages"][-1]
    ic(ai_message)

    human_response = (
        "We, the experts are here to help! We'd recommend you check out LangGraph to build your agent."
        " It's much more reliable and extensible than simple autonomous agents."
    )

    tool_message = create_response(human_response, ai_message)
    graph.update_state(config, {"messages": [tool_message]})

    snapshot = graph.get_state(config=config)
    ic(snapshot)

    ic(" - - - - - - - - - - - - - - After Human Response - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ")

    ic(" - - - - - - - - - - - - - - Resume the graph by invoking it with None as the inputs - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ")
    time.sleep(3)
    events = graph.stream(None, config, stream_mode="values")
    for event in events:
        if "messages" in event:
            ic(event["messages"][-1])

