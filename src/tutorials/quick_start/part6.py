
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

#https://langchain-ai.github.io/langgraph/tutorials/introduction/#part-6-customizing-state
class GraphPart6_2():
    def __init__(self, threadId:str):
        ic("def graphPart6.init")
        self.memory = MemorySaver()
        self.config = {"configurable": {"thread_id": threadId}}


    def create_response(self, response: str, ai_message: AIMessage):
        ic("create_response")
        return ToolMessage(
            content=response,
            tool_call_id=ai_message.tool_calls[0]["id"],
        )
    
    def compile_graph(self):
        ic("def graphPart6.compileGraph")

        # Updated State object . . with ask_human node
        class State(TypedDict):
            messages: Annotated[list, add_messages]
            # This flag is new
            ask_human: bool

        # define a schema to show the model to let it decide to request assistance.
        class RequestAssistance(BaseModel):
            ic("RequestAssistance")

            """Escalate the conversation to an expert. Use this if you are unable to assist directly or if the user requires support beyond your permissions.
            To use this function, relay the user's 'request' so the expert can provide the right guidance.
            """
            request: str

        # Next, define the chatbot node. The primary modification here is flip the ask_human flag
        # if we see that the chat bot has invoked the RequestAssistance flag.
        tool = TavilySearchResults(max_results=2)
        tools = [tool]
        llm = ChatGroq()

        # We can bind the llm to a tool definition, a pydantic model, or a json schema
        llm_with_tools = llm.bind_tools(tools + [RequestAssistance])


        def chatbot(state: State):
            ic("in chatbot")
            response = llm_with_tools.invoke(state["messages"])
            ask_human = False
            ic(response)
            if (
                response.tool_calls
                and response.tool_calls[0]["name"] == RequestAssistance.__name__
            ):
                ask_human = True
            return {"messages": [response], "ask_human": ask_human}

        # Next, create the graph builder and add the chatbot and tools nodes to the graph, same as before.
        graph_builder = StateGraph(State)

        graph_builder.add_node("chatbot", chatbot)
        graph_builder.add_node("tools", ToolNode(tools=[tool]))

        # Next, create the "human" node. 
        # This node function is mostly a placeholder in our graph that will trigger an interrupt.
        # If the human does not manually update the state during the interrupt,
        #  it inserts a tool message so the LLM knows the user was requested but didn't respond.
        #  This node also unsets the ask_human flag so the graph knows not to revisit the node unless further requests are made.
        '''
        def create_response(response: str, ai_message: AIMessage):
            ic("create_response")
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
                    self.create_response("No response from human.", state["messages"][-1])
                )
            return {
                # Append the new messages
                "messages": new_messages,
                # Unset the flag
                "ask_human": False,
            }


        graph_builder.add_node("human", human_node)

        # Next, define the conditional logic. The select_next_node will route to the human node if the flag is set.
        # Otherwise, it lets the prebuilt tools_condition function choose the next node.

        # Recall that the tools_condition function simply checks to see if the chatbot has responded with any tool_calls in its response message.
        # If so, it routes to the action node. Otherwise, it ends the graph.
        def select_next_node(state: State):
            if state["ask_human"]:
                return "human"
            # Otherwise, we can route as before
            return tools_condition(state)


        graph_builder.add_conditional_edges(
            "chatbot",
            select_next_node,
            {"human": "human", "tools": "tools", "__end__": "__end__"},
        )
        
        
        # Finally, add the simple directed edges and compile the graph.
        # These edges instruct the graph to always flow from node a->b whenever a finishes executing.
        graph_builder.add_edge("tools", "chatbot")
        graph_builder.add_edge("human", "chatbot")
        graph_builder.set_entry_point("chatbot")

        memory = MemorySaver()

        self.graph = graph_builder.compile(
            checkpointer=memory,
            interrupt_before=["human"],
        )


    def getStream(self, user_input:str):
        ic(f"def graphPart6.getStream, self.config is ${self.config}")
        events = self.graph.stream({"messages": [("user", user_input)]}, self.config, stream_mode="values")
        return events
    
    # Passing in None will just let the graph continue where it left off, without adding anything new to the state
    def getStreamWithNone(self):
        ic(f"def graphPart6.getStreamWithNone")
        events = self.graph.stream(None, self.config, stream_mode="values")
        return events


    def getSnapshot(self):
        ic("def graphPart6.getSnapshot")
        return self.graph.get_state(self.config)

    # The update_state function operates as if it were one of the nodes in your graph!
    # By default, the update operation uses the node that was last executed, but you can manually specify it below.
    def updateState(self, new_messages):
        ic("def graphPart6.updateState")
        self.graph.update_state(
            self.config,
            {"messages": new_messages},
        )

        return self.graph.get_state(self.config)

    def updateStateWithNodeDefined(self, messages, as_node):
        ic("def graphPart6.updateStateWithNodeDefined")
        self.graph.update_state(
            self.config,
            {"messages": messages},
            # Which node for this function to act as. It will automatically continue
            # processing as if this node just ran.
            as_node=as_node
        )

        return self.graph.get_state(self.config)














    


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

