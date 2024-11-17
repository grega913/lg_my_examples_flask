from icecream import ic
import secrets
import string
from flask import request, url_for, redirect, render_template
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
    # ic(f"detect_message_type: ${message}")

    if isinstance(message, HumanMessage):
        return {"role": "user", "content": message.content}
    elif isinstance(message, ToolMessage):
        return {"role": "tool", "content": message.content}
    elif isinstance(message, AIMessage):
        return {"role": "ai", "content": message.content}
    else:
        return {"role": "unknown", "content": None}
    

def check_snapshot_next(snapshot):
    ic("def check_snapshot_next")
    return snapshot.next == ('tools',)

def check_snapshot_next_human(snapshot):
    ic("def check_snapshot_next")
    return snapshot.next == ('human',)


# function called when route part4_2 is selected
def routingInPart4_2(request, session, graphPart4):
    ic("def routingInPart4_2")
    ic(session)
    ic(request)
    ic(graphPart4)

    if request.method == "POST":
        ic("request is POST")

        users_input = request.form.get('input_field_graphPart4')
        ic(users_input)



        return redirect(url_for('quick_start', path = "part4_2"))
    else:
        ic("request is GET")

        return render_template('quick_start/part4_2.html', user = session['user'], messages = session['messages'])


def extract_messages_from_snapshot(snapshot):
    ic("def extract_messages_from_values")
    return snapshot.values["messages"]





