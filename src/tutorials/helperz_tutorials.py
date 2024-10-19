from icecream import ic

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
