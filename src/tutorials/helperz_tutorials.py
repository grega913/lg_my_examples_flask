from icecream import ic
import secrets
import string

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

def stream_graph_updates(graph, user_input: str):
    ic("def stream_graph_updates")
    for event in graph.stream({"messages": [("user", user_input)]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)






def proceedWithNone(graph, config):
    ic("def proceedWithNone")
    if graph:

        events = graph.stream(None, config, stream_mode="values")
        for event in events:
            if "messages" in event:
                event["messages"][-1].pretty_print()



def createRandomString():
    ic("def createRandomString")
    length = 16
    random_string = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(length))
    ic(random_string)
    return random_string



def detect_message_type(message):
    if isinstance(message, HumanMessage):
        return {"role": "user", "content": message.content}
    elif isinstance(message, ToolMessage):
        return {"role": "tool", "content": message.content}
    elif isinstance(message, AIMessage):
        return {"role": "ai", "content": message.content}
    else:
        return {"role": "unknown", "content": None}
