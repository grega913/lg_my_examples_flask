# https://colab.research.google.com/drive/1QqOqd7M10FcWSQ0IzXcbBV-001y5TMI5#scrollTo=4iZQS3sJDAsm

# notes - works on ChatOpenAi but not on ChatGroq

import os
import sys
from icecream import ic
from pprint import pprint
import time
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage, RemoveMessage
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END

dir_path = os.path.dirname(os.path.abspath(__file__))
path_academy = os.path.dirname(dir_path)
sys.path.append(path_academy)

ic(dir_path)
ic(path_academy)

from helperz_academy import multiply, add, divide, State, call_model, summarize_conversation, should_continue
from scripts_academy import system_script1


class AcGraphM2L5():
    def __init__(self, threadId:str = ""):
        ic("initializing AcGraphM2L5")
        self.config = {"configurable": {"thread_id": threadId}}


    def compile_graph(self):
        # Define a new graph
        workflow = StateGraph(State)
        workflow.add_node("conversation", call_model)
        workflow.add_node(summarize_conversation)

        # Set the entrypoint as conversation
        workflow.add_edge(START, "conversation")
        workflow.add_conditional_edges("conversation", should_continue)
        workflow.add_edge("summarize_conversation", END)

        # Compile
        memory = MemorySaver()
        graph = workflow.compile(checkpointer=memory)

        self.graph = graph

        return graph 


    def invokeGraph(self, message):
        ic(f"invokeGraph ${message}")
        response = self.graph.invoke({"messages": message}, config= self.config)
        '''
        for m in response['messages']:
            pprint(m)
        '''
        return response
    
    def getSummary(self):
        ic("def getSummary")
        response = self.graph.get_state(self.config).values.get("summary","")
        return response
    
    def getMessages(self):
        ic("def getMessages")
        response = self.graph.get_state(self.config).values.get("messages","")
        return response

    
    
if __name__ == "__main__":
    ic("name = main in M2Lesson5")

    agent = AcGraphM2L5(threadId="M2L5")
    agent.compile_graph()

    # Step 1
    input_message = HumanMessage(content="hi! I'm Lance")
    output = agent.invokeGraph(input_message)
    for m in output['messages'][-1:]:
        m.pretty_print()
    
    print("#" * 25)

    # Step 2
    input_message = HumanMessage(content="what's my name?")
    output = agent.invokeGraph(input_message)
    for m in output['messages'][-1:]:
        m.pretty_print()

    print("#" * 25)

    # Step 3
    input_message = HumanMessage(content="i like the 49ers!")
    output = agent.invokeGraph(input_message)
    for m in output['messages'][-1:]:
        m.pretty_print()
    
    print("#" * 25)
    print("Summary:")
    ic(f"summary: ${agent.getSummary()}")

    # Step 4
    input_message = HumanMessage(content="i also like LA Lakers!")
    output = agent.invokeGraph(input_message)
    for m in output['messages'][-1:]:
        m.pretty_print()
    
    print("#" * 25)
    print("Summary:")
    ic(f"summary: ${agent.getSummary()}")

    # Step 5
    input_message = HumanMessage(content="i also like Chicago Bulls! in fact, I love them the most.")
    output = agent.invokeGraph(input_message)
    for m in output['messages'][-1:]:
        m.pretty_print()
    
    print("#" * 25)
    print("Summary:")
    ic(f"summary: ${agent.getSummary()}")
