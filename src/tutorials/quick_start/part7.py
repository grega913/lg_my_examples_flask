
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





class GraphPart7:

    def __init__(self):
        ic("initializing GraphPart7")
        
        
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

        
        def create_response(response: str, ai_message: AIMessage):
            ic("def create_response")
            ic(ai_message.tool_calls[0]["id"])

            return ToolMessage(
                content=response,
                tool_call_id=ai_message.tool_calls[0]["id"],
            )
        

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
            {"human": "human", "tools": "tools", END: END},
        )
        self.graph_builder.add_edge("tools", "chatbot")
        self.graph_builder.add_edge("human", "chatbot")
        self.graph_builder.add_edge(START, "chatbot")

        memory = MemorySaver()

        self.graph = self.graph_builder.compile(
            checkpointer=memory,
            interrupt_before=["human"],
        )



if __name__=="__main__":
    ic(" defmain in part7")

    graphPart7 = GraphPart7()
    graph = graphPart7.graph

    config = {"configurable": {"thread_id": "1"}}
    events = graph.stream(
        {
            "messages": [
                ("user", "I'm learning LangGraph. Could you do some research on it for me?")
            ]
        },
        config,
        stream_mode="values",
    )
    for event in events:
        if "messages" in event:
            ic(event["messages"][-1])
    
    
    events = graph.stream(
    {
        "messages": [
            ("user", "Ya that's helpful. Maybe I'll build an autonomous agent with it!")
        ]
    },
    config,
    stream_mode="values",
    )
    for event in events:
        if "messages" in event:
            ic(event["messages"][-1])
    ic(" - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")

    to_replay = None
    for state in graph.get_state_history(config):
        ic("Num Messages: ", len(state.values["messages"]), "Next: ", state.next)
        print("-" * 80)
        if len(state.values["messages"]) == 6:
            # We are somewhat arbitrarily selecting a specific state based on the number of chat messages in the state.
            to_replay = state

    ic(to_replay.next)
    ic(to_replay.config)

    # The `checkpoint_id` in the `to_replay.config` corresponds to a state we've persisted to our checkpointer.
    for event in graph.stream(None, to_replay.config, stream_mode="values"):
        if "messages" in event:
            ic(event["messages"][-1])
