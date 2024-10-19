
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

from icecream import ic




def part5_compile_graph():
    ic("def part5_compile_graph")

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
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")
    memory = MemorySaver()
    graph = graph_builder.compile(
        checkpointer=memory,
        # This is new!
        interrupt_before=["tools"],
        # Note: can also interrupt **after** actions, if desired.
        # interrupt_after=["tools"]
    )

    return graph




class GraphPart5:

    def __init__(self):
        ic("initializing GraphPart5")

        class State(TypedDict):
            messages: Annotated[list, add_messages]

        
        self.graph_builder = StateGraph(State)

        tool = TavilySearchResults(max_results=2)
        tools = [tool]
        llm = ChatGroq()
        llm_with_tools = llm.bind_tools(tools)
        memory = MemorySaver()

        def chatbot(state: State):
            return {"messages": [llm_with_tools.invoke(state["messages"])]}

        self.graph_builder.add_node("chatbot", chatbot)

        tool_node = ToolNode(tools=[tool])
        self.graph_builder.add_node("tools", tool_node)

        self.graph_builder.add_conditional_edges(
            "chatbot",
            tools_condition,
        )
        self.graph_builder.add_edge("tools", "chatbot")
        self.graph_builder.add_edge(START, "chatbot")
        

        self.graph = self.graph_builder.compile(
            checkpointer=memory,
            interrupt_before=["tools"],
        )

    def stream(self, user_input, config):
        ic("in GraphPart5")
        events = self.graph.stream({"messages": [("user", user_input)]}, config)
        for event in events:
            if "messages" in event:
                ic(event["messages"][-1])


    def updateGraphState(self, config, new_messages):
        ic("updateState in GraphPart5")
        self.graph.update_state(
            config,
            {"messages": new_messages}
        )
    
    def getSnapshot(self, config):
        return self.graph.get_state(config)
    

    


# In your route







if __name__ == "__main__":
    ic("def main")

    graph_part5 = part5_compile_graph()
    ic("we have graph_part5")

    user_input = "I'm learning LangGraph. Could you do some research on it for me?"
    config = {"configurable": {"thread_id": "1"}}
    # The config is the **second positional argument** to stream() or invoke()!
    events = graph_part5.stream({"messages": [("user", user_input)]}, config)
    for event in events:
        if "messages" in event:
            ic(event["messages"][-1])
    ic(" - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  ")
    snapshot = graph_part5.get_state(config=config)
    ic(snapshot)
    ic(" - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  ")
    existing_message = snapshot.values["messages"][-1]
    ic(existing_message)
    ic(" - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  ")

    answer = ("LangGraph is a library for building stateful, multi-actor applications with LLMs.")
    new_messages = [
        # The LLM API expects some ToolMessage to match its tool call. We'll satisfy that here.
        ToolMessage(content=answer, tool_call_id=existing_message.tool_calls[0]["id"]),
        # And then directly "put words in the LLM's mouth" by populating its response.
        AIMessage(content=answer),
    ]
    ic(len(new_messages))
    last_message = new_messages[-1]

    ic(last_message)

    # update state with new messages that contain our answer
    time.sleep(3)
    ic("we'll be updating state")
    graph_part5.update_state(
        # Which state to update
        config,
        # The updated values to provide. The messages in our `State` are "append-only", meaning this will be appended
        # to the existing state. We will review how to update existing messages in the next section!
        {"messages": new_messages},
    )

    ic("\n\nLast 2 messages;")
    ic(graph_part5.get_state(config).values["messages"][-2:])

    ic(" - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  ")

    time.sleep(3)
    
    
    graph_part5.update_state(
        config,
        {"messages": [AIMessage(content="I'm an AI expert!")]},
        # Which node for this function to act as. It will automatically continue
        # processing as if this node just ran.
        as_node="chatbot",
    )

    snapshot = graph_part5.get_state(config)
    ic(snapshot.values["messages"][-3:])
    ic(snapshot.next)

    ic(" - - - - - - - - - - - END - - - - - - - - -")

    # What if we want to overwrite existing messages?

    ic(" - - - - - - - - - - - - - - - - - - - - - - ")
    ic(" - - - let's try with thread_id = 2")

    user_input = "I'm learning LangGraph. Could you do some research on it for me?"
    config = {"configurable": {"thread_id": "2"}}  # we'll use thread_id = 2 here
    events = graph_part5.stream(
        {"messages": [("user", user_input)]}, config, stream_mode="values"
    )
    for event in events:
        if "messages" in event:
            ic(event["messages"][-1])
    



    snapshot = graph_part5.get_state(config)
    existing_message = snapshot.values["messages"][-1]
    ic("Original")
    ic("Message ID", existing_message.id)
    ic(existing_message.tool_calls[0])
    new_tool_call = existing_message.tool_calls[0].copy()
    new_tool_call["args"]["query"] = "LangGraph human-in-the-loop workflow"
    new_message = AIMessage(
        content=existing_message.content,
        tool_calls=[new_tool_call],
        # Important! The ID is how LangGraph knows to REPLACE the message in the state rather than APPEND this messages
        id=existing_message.id,
    )

    ic("Updated")
    ic(new_message.tool_calls[0])
    ic("Message ID", new_message.id)
    graph_part5.update_state(config, {"messages": [new_message]})

    ic("\n\nTool calls")
    graph_part5.get_state(config).values["messages"][-1].tool_calls

    events = graph_part5.stream(None, config, stream_mode="values")
    for event in events:
        if "messages" in event:
           ic(event["messages"][-1])

    events = graph_part5.stream(
    {
        "messages": (
            "user",
            "Remember what I'm learning about?",
        )
    },
    config,
    stream_mode="values",
    )
    for event in events:
        if "messages" in event:
            ic(event["messages"][-1])



    




    

