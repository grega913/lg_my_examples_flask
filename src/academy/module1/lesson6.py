# https://colab.research.google.com/drive/1edfeQ7pjoUnfZns0AEgPrjRy_AUQcF-p#scrollTo=b517142d-c40c-48bf-a5b8-c8409427aa79

# notes - works on ChatOpenAi but not on ChatGroq

import os
import sys
from icecream import ic
from pprint import pprint
import time
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode

dir_path = os.path.dirname(os.path.abspath(__file__))
path_academy = os.path.dirname(dir_path)
sys.path.append(path_academy)


ic(dir_path)
ic(path_academy)

from helperz_academy import multiply, add, divide
from scripts_academy import system_script1



class AcGraphM1L6():
    def __init__(self, threadId:str = ""):
        ic("initializing SimpleAgentWithTools")
        self.config = {"configurable": {"thread_id": threadId}}



    def compile_graph(self):

        # tools
        tools = [multiply, add, divide]

        # llm
        llm = ChatOpenAI()
        llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

        # System message
        sys_msg = SystemMessage(content=system_script1)

        # Node
        def assistant(state: MessagesState):
            ic("assistant working . . .")
            return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

        # Graph
        builder = StateGraph(MessagesState)

        # Define nodes: these do the work
        builder.add_node("assistant", assistant)
        builder.add_node("tools", ToolNode(tools))

        # Define edges: these determine how the control flow moves
        builder.add_edge(START, "assistant")
        builder.add_conditional_edges(
            "assistant",
            # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
            # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
            tools_condition,
        )
        builder.add_edge("tools", "assistant")
        graph = builder.compile()

        self.graph = graph
        return graph 


    def invokeGraph(self, message):
        ic(f"invokeGraph ${message}")
        response = self.graph.invoke({"messages": message})

        for m in response['messages']:
            pprint(m)
        return response
    
    
    




if __name__=="__main__":
    ic("name=main in l6_Agent")



    agent = AcGraphM1L6()
    agent.compile_graph()
    
    messages = [HumanMessage(content="Add 30 and 40. Multiply the output by 5. Divide the output by 4")]
    ic(messages)

    response = agent.invokeGraph(message=messages)

    ic(response)

    for m in response['messages']:
        m.pretty_print()
