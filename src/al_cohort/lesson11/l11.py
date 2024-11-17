# LangGraph Agents https://app.alejandro-ao.com/lessons/langgraph-agents/

from langgraph.graph import StateGraph, START, END, MessageGraph, MessagesState
from typing_extensions import TypedDict
import matplotlib.pyplot as plt
import random
from typing import Literal
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from pprint import pprint
from icecream import ic
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
import os
import sys
from pprint import pprint


from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, ToolMessage

dir_path = os.path.dirname(os.path.abspath(__file__))
ic(dir_path)
sys.path.append(dir_path)

from l11_helperz import multiply_numbers, decide_node, node_1, node_2, node_3, State, get_temperature, convert_to_fahrenheit

llm = ChatGroq(model = "llama-3.1-70b-versatile")

# region simplestGraph
def simplest_graph():
    # initialize State
    builder = StateGraph(State)

    #add nodes
    builder.add_node("node_1", node_1)
    builder.add_node("node_2", node_2)


    # add edges
    builder.add_edge(START, "node_1")
    builder.add_edge("node_1", "node_2")
    builder.add_edge("node_2", END)

    # build/compile graph
    graph = builder.compile()

    return graph

# endregion


# region graph_with_conditional_node
def graph_with_conditional_node():

    def decide_node(state:State) -> Literal["node_2", "node_3"]:  # the return value of decision function is either "node_2" or "node_3". So we need to return a Literal
        print("decide_node")
        print(state)
        return random.choice(["node_2", "node_3"])
    
    # initialize State
    builder = StateGraph(State)

    #add nodes
    builder.add_node("node_1", node_1)
    builder.add_node("node_2", node_2)
    builder.add_node("node_3", node_3) # this is new


    # add edges
    builder.add_edge(START, "node_1")
    builder.add_conditional_edges("node_1", decide_node)
    # builder.add_edge("node_1", "node_2")
    builder.add_edge("node_2", END)
    builder.add_edge("node_3", END)

    # build/compile graph
    graph = builder.compile()

    return graph

# endregion


# region graph_with_tool_calling_agent

# define tools - currently tools are just a array with a single record - a function
tools = [multiply_numbers]

# bind the tools to the llm so the llm knows it can use tools
llm_with_tools = llm.bind_tools(tools)



'''
class GraphLesson11():

    def __init__(self, threadId:str):
        ic("def graphLesson11.init")
        self.config = {"configurable": {"thread_id": threadId}}


    def compile_graph(self):
        ic("def graphPart11.compile_graph")

        builder = StateGraph(State)

        #add nodes
        builder.add_node("node_1", node_1)
        builder.add_node("node_2", node_2)
        builder.add_node("node_3", node_3)


        # add edges
        builder.add_edge(START, "node_1")
        builder.add_conditional_edges("node_1", decide_node)
        # builder.add_edge("node_1", "node_2")
        builder.add_edge("node_2", END)
        builder.add_edge("node_3", END)

        # build/compile graph
        graph = builder.compile()

        self.graph=graph
        
        return graph

    
    def getStream(self, user_input:str):
        ic(f"def graphPart11.getStream, self.config is ${self.config}")
        events = self.graph.stream({"messages": [("user", user_input)]}, self.config, stream_mode="values")
        return events
    

    def graphInvoke(self, user_input:str):
        ic("def graphInvoke")
        response = self.graph.invoke({"my_state": user_input })
        ic(response)
        return response
    
    
    # Passing in None will just let the graph continue where it left off, without adding anything new to the state
    def getStreamWithNone(self):
        ic(f"def graphPart5.getStreamWithNone")
        events = self.graph.stream(None, self.config, stream_mode="values")
        return events


    def getSnapshot(self):
        ic("def graphPart5.getSnapshot")
        return self.graph.get_state(self.config)

    # The update_state function operates as if it were one of the nodes in your graph!
    # By default, the update operation uses the node that was last executed, but you can manually specify it below.
    def updateState(self, new_messages):
        ic("def graphPart5.updateState")
        self.graph.update_state(
            self.config,
            {"messages": new_messages},
        )

        return self.graph.get_state(self.config)

    def updateStateWithNodeDefined(self, messages, as_node):
        ic("def graphPart5.updateStateWithNodeDefined")
        self.graph.update_state(
            self.config,
            {"messages": messages},
            # Which node for this function to act as. It will automatically continue
            # processing as if this node just ran.
            as_node=as_node
        )

        return self.graph.get_state(self.config)
'''






''' We have a Graph that has a LM node within it. Sometimes it returns function calls and sometimes it returns regular messages.
# We should make a conditional edge:
1. - either go to function call, or
2. - go to end message

We need to have a node that executes a function, that is returned by LLM.
LangGraph comes with a prebuild node that will automatically execute function call that agent contains. Let's rebuild the graph.

1.  ToolNode - a node that runs the tools in the last message
2.  tools_condition:
    - identifies last message
    - if the last message has tool calls we will execute them, otherwise return END

'''

class GraphLesson11():

    def __init__(self, threadId:str):
        ic("def GraphLesson11_withToolNode.init")
        self.config = {"configurable": {"thread_id": threadId}}
    
    '''
    def compile_graph_with_single_llm_node(self):
        ic("def graphPart11.compile_graph")

        #builder = StateGraph(State)
        builder = StateGraph(MessagesState)

        
        # add nodes
        builder.add_node("llm_node", llm_node)

        # add edges
        builder.add_edge(START, "llm_node")
        builder.add_edge("llm_node", END)

        # compile a builder
        graph = builder.compile()

        self.graph=graph
        
        return graph
    '''

    def compile_graph(self):
        ic("def graphPart11.compile_graph_with_tool_node")
        # create nodes - we are using a type of MessagesState -> only defining a single node
        
        def multiply(a: int, b: int) -> int:
            """
            Multiply two numbers.
            Args:
                a: int
                b: int
            """
            return a * b
        
        tools = [multiply]
        llm_with_tools = llm.bind_tools(tools=tools)

        def llm_node(state: MessagesState) -> MessagesState:
            print()
            print("#" * 80)
            print("ENTERING LLM NODE")
            print(state)
            response = llm_with_tools.invoke(state["messages"])
            print("#" * 80)
            print("EXITING LLM NODE")
            return {"messages": [response]}


        builder = StateGraph(MessagesState)
                
        # add nodes
        builder.add_node("llm_node", llm_node)
        builder.add_node("tools", ToolNode(tools=tools))

        # add edges
        builder.add_edge(START, "llm_node")
        builder.add_conditional_edges("llm_node", tools_condition)
        builder.add_edge("tools", END)

        # compile a builder
        graph = builder.compile()

        self.graph=graph
        
        return graph


    def invokeGraph11(self, message):
        ic(f"invoke Graph11 ${message}")
        response = self.graph.invoke({"messages": message})

        for m in response['messages']:
            pprint(m)
        return response
    

# https://app.alejandro-ao.com/topics/build-a-react-agent-in-langgraph/
class GraphLesson11_MultipleTools():
        
        def __init__(self, threadId:str):
            ic("def GraphLesson11_withToolNode.init")
            self.config = {"configurable": {"thread_id": threadId}}

        def compile_graph_multiple_tools(self):
            ic("def graphPart11.compile_graph_with_tool_node")
            # create nodes - we are using a type of MessagesState -> only defining a single node
        

        
            tools = [get_temperature, convert_to_fahrenheit]
            llm = ChatOpenAI(model="gpt-4o-mini")
            llm_with_tools = llm.bind_tools(tools=tools)

            def llm_node(state: MessagesState) -> MessagesState:
                print()
                print("#" * 80)
                print("ENTERING LLM NODE")
                print(state)
                response = llm_with_tools.invoke(state["messages"]) # calling our history of messages
                print("#" * 80)
                print("EXITING LLM NODE")
                return {"messages": [response]}


            builder = StateGraph(MessagesState)
                    
            # add nodes
            builder.add_node("llm_node", llm_node)
            builder.add_node("tools", ToolNode(tools=tools))

            # add edges
            builder.add_edge(START, "llm_node")
            builder.add_conditional_edges("llm_node", tools_condition)
            #builder.add_edge("tools", END) # before
            builder.add_edge("tools", "llm_node") # after

            # compile a builder
            graph = builder.compile()

            self.graph=graph
            
            return graph
        
        def invokeGraph11_multiple_tools(self, message):
            ic(f"invoke Graph11 ${message}")
            response = self.graph.invoke({"messages": message})

            for m in response['messages']:
                pprint(m)
            return response



# endregion

if __name__=="__main__":

    # simplest graph example
    # graph = simplest_graph()

    
    # example with graph_with_conditional_node:
    # graph = graph_with_conditional_node()

    # response = graph.invoke({"my_state": "Hello, I am Johhnnyy. "})
    # print(response)

    # response = llm.invoke("Hello, how are you?")
    '''
    response = llm.invoke("What is 523*780236?")  # simple graph without access to tool_calls
    response.pretty_print()
    pprint(response.__dict__) # we have content, but the "tool_calls" is empty

    print(" - - - - - ")

    # this model has access to tools and uses them when it needs to
    response = llm_with_tools.invoke("What is 523*780236?")
    response.pretty_print()
    pprint(response.__dict__)
    # content of the response is empty, but we have tool_calls object
    '''

    '''

    response = llm_node({"messages": ["what is 523*780236"]})
    ic(response)


    # example where we pass something that requires a function call
    message1 = [
        ("user","what is 523*780236?")
    ]

    # example whre we pass something that does not require a function call
    message2 = [
        ("system", "You are a detective. Always answer sarcastically"),
        ("user", "how do you solve a mistery")
    ]


    graphLesson11 = GraphLesson11_withToolNode(threadId="11")
    graphLesson11.compile_graph_with_single_llm_node()


    final1 = graphLesson11.graph.invoke({"messages": message1})
    final2 = graphLesson11.graph.invoke({"messages": message2})

    
    for m in final1["messages"]:
        m.pretty_print()

    for m in final2["messages"]:
        m.pretty_print()

    print(" - - - - - - - - - - - - - - - - - - - - - - - ")
    print(" - - - - - - - - - - - - - - - - - - - - - - - ")
    print(" - - - - - - - - - - - - - - - - - - - - - - - ")
    print(" - - - - - - - - - - - - - - - - - - - - - - - ")


    '''

    message1 = [
    ("system", "You are a Sherlock Holmes. Always answer sarcastically"),
    ("user", "how do you solve a mistery")
    ]

    message2 = [
    ("user", "What is 523*780236"),
    ]


    ########################################################################################## 
    
    # This is the example where we only have a single tool
    '''

    graphLesson11= GraphLesson11(
    threadId="3"
    )
    graphLesson11.compile_graph()

    # using a single tool - calculate 
    response3 = graphLesson11.invokeGraph11(message=message1) # without the need to call a tool
    response4 = graphLesson11.invokeGraph11(message=message2) # with a tool call


'''

##################################################################################################

# Example where we use AGnet with access to multiple tools

    graphLesson11_multiple_tools= GraphLesson11_MultipleTools(
        threadId="3"
    )
    graphLesson11_multiple_tools.compile_graph_multiple_tools()


    message = [
    ("system", "You are a Sherlock Holmes. Always answer sarcastically"),
    ("user", "how do you solve a mistery")
    ]
    response = graphLesson11_multiple_tools.invokeGraph11_multiple_tools(message=message) # without the need to call a tool
    for m in response['messages']:
        pprint(m)
        

    print(" - - - - - - - - - - - ")



    
    
    # make it use a tool
    message4 = [
        ("user", "What is the temperature in New York in Fahrenheit")
    ]
    response4 = graphLesson11_multiple_tools.invokeGraph11_multiple_tools(message=message4)
    for m in response4['messages']:
        pprint(m)

