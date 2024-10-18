from icecream import ic

def stream_graph_updates(graph, user_input: str):
    ic("def stream_graph_updates")
    for event in graph.stream({"messages": [("user", user_input)]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)