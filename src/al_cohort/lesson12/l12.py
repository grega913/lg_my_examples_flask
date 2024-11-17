
#Agent with memory

# https://colab.research.google.com/drive/1OF40KJllQAFfvX2hAh2rbW3-nVYq6PqF#scrollTo=84TmFLBONq2p
# https://app.alejandro-ao.com/topics/agent-with-memory/

from icecream import ic

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from pprint import pprint
from IPython.display import Image, display
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, RemoveMessage
from typing import Literal
import time
import os
import sys

dir_path = os.path.dirname(os.path.abspath(__file__))
ic(dir_path)
sys.path.append(dir_path)

from l12_helperz import multiply, sum, chat, summarize_conversation, should_summarize, State


# Simple graph with memory
class GraphLesson12_1():

    def __init__(self, threadId:str):
        ic("def graphLesson12_1.init")
        self.config = {"configurable": {"thread_id": threadId}}
    

    def compile_graph(self):

        tools = [multiply, sum]

        llm = ChatOpenAI()
        llm_with_tools = llm.bind_tools(tools=tools)

        # node
        def llm_node(state: MessagesState) -> MessagesState:
            response = llm_with_tools.invoke(state["messages"])
            return {"messages": [response]} 

        # initialize a builder
        builder = StateGraph(MessagesState)

        # add nodes
        builder.add_node("llm_node", llm_node)
        builder.add_node("tools", ToolNode(tools))


        # add edges
        builder.add_edge(START, "llm_node")
        builder.add_conditional_edges("llm_node", tools_condition)
        builder.add_edge("tools", "llm_node")

        # add memory -> new stuff here
        memory = MemorySaver() # storing entire state in memory

        # compile a builder
        
        graph = builder.compile(checkpointer=memory)

        self.graph = graph
        return graph 


    def invokeGraph12(self, message):
        ic(f"invoke Graph11 ${message}")
        response = self.graph.invoke({"messages": message}, config=self.config)

        for m in response['messages']:
            pprint(m)
        return response
    
    


    
    def getState(self):
        return self.graph.get_state(self.config)

# Graph with Summaarization
class GraphLesson12_2():
    def __init__(self, threadId:str):
        ic("def graphLesson12_2.init")
        self.config = {"configurable": {"thread_id": threadId}}
    

    def compile_graphLesson12_2(self):
        ic("def compile_graphLesson12_2")

        builder = StateGraph(State)

        builder.add_node("chat", chat)
        builder.add_node("summarize_conversation", summarize_conversation)

        builder.add_edge(START, "chat")
        builder.add_conditional_edges("chat", should_summarize)
        builder.add_edge("summarize_conversation", END)

        memory = MemorySaver()

        graph = builder.compile(checkpointer=memory)
        # add memory -> new stuff here
        memory = MemorySaver() # storing entire state in memory

        # compile a builder
        
        graph = builder.compile(checkpointer=memory)

        self.graph = graph

        return graph 


    def invokeGraph12_2(self, message):
        ic(f"invoke Graph12_2 ${message}")
        response = self.graph.invoke({"messages": message}, config=self.config)
        '''
        for m in response['messages']:
            pprint(m)
        '''
        return response
    

    def streamGraph12_2(self, message):
        ic(f"streamGraph12_2")
        response = self.graph.stream({"messages": message}, config=self.config)
        return response


    def getState(self):
        ic("def getState and self.config is ${self.config}")
        return self.graph.get_state(self.config)


def get_messages_and_summary(state):
    if 'messages' in state.values and state.values['messages']:
        messages = state.values['messages']
    else:
        messages = None

    if 'summary' in state.values and state.values['summary']:
        summary = state.values['summary']
    else:
        summary = None

    return messages, summary



def testPart1():
    ic("testPart1")
    graphLesson12 = GraphLesson12_1(threadId=1)
    graphLesson12.compile_graph()

    # Step 1
    message = "What is 500 plus 565?"
    graphLesson12.invokeGraph12(message = message)
    state = graphLesson12.getState()
    '''for m in state.values.get("messages", []):
        m.pretty_print()
    '''
    print("*" * 80)

    # Step 2    
    message = "Multiply that by 10?"
    graphLesson12.invokeGraph12(message = message)
    state = graphLesson12.getState()

    for m in state.values.get("messages", []):
        m.pretty_print()


def testPart2():
    ic("def testPart2")
    graphLesson12_2 = GraphLesson12_2(threadId=2)
    graphLesson12_2.compile_graph()

    # Step 1
    input_message = HumanMessage(content="Hello, my name is Bojan Kopač, but everyone calls me Bojchi?")
    response = graphLesson12_2.invokeGraph12_2(message = input_message)
    state = graphLesson12_2.getState()
    ic(response)
    ic(state)
    print("#" * 20 + " end of part 1")
    time.sleep(1)


    # Step 2
    input_message = HumanMessage(content="What is my name?")
    response = graphLesson12_2.invokeGraph12_2(message = input_message)
    state = graphLesson12_2.getState()
    ic(response)
    ic(state)

    print("#" * 20 + " end of part 2")
    time.sleep(1)
    # Step 3
    input_message = HumanMessage(content="Do you know who I am")
    response = graphLesson12_2.invokeGraph12_2(message = input_message)
    state = graphLesson12_2.getState()
    ic(response)
    ic(state)
    print("#" * 20 + " end of part 3")
    time.sleep(1)
    
    





if __name__ == "__main__":
    ic("name is main in l12.py")

    #testPart1()
    testPart2()


