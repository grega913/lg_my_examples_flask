from flask import Flask, session, url_for, request, render_template, jsonify
from flask_socketio import SocketIO
from icecream import ic
import time
import sys
import os

from langchain_core.messages import AIMessage, ToolMessage

from tutorials.helperz_tutorials import stream_graph_updates, proceedWithNone
from tutorials.quick_start.part1 import part1_compile_graph, part1_stream_graph
from tutorials.quick_start.part2 import part2_compile_graph
from tutorials.quick_start.part3 import part3_compile_graph
from tutorials.quick_start.part4 import part4_compile_graph
from tutorials.quick_start.part5 import GraphPart5
from tutorials.quick_start.part7 import GraphPart7

from playground.playground import square_numbers


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

graph_part4 = part4_compile_graph()


# graph as Class
graphPart5 = GraphPart5()
graphPart7 = GraphPart7()



# region Routes
@app.route('/index')
def index(name="Default Name"):
    return render_template('index.html', name=name)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route("/playground")
def playground():
    return render_template('playground.html')

@app.route('/lg_tutorials/quick_start/<path:path>')
def quick_start(path):
    if path =="part1":
        return render_template('quick_start/part1.html')
    elif path =="part2":
       return render_template('quick_start/part2.html')
    elif path == "part3":
        return render_template('quick_start/part3.html')
    elif path == "part4":
        return render_template('quick_start/part4.html')
    elif path == "part5":
        return render_template('quick_start/part5.html')
    elif path == "part6":
        return render_template('quick_start/part6.html')
    elif path == "part7":
        return render_template('quick_start/part7.html')
    else:
        return f'Check path name'


#api routes
@app.route('/api/quick_start/part1', methods= ['POST'])
def api_part1():
    ic("api_part1")
    ic(request)
    ic(request.get_json())
    user_input = request.get_json()['user_input']
    ic(user_input)

    graph_part1 = part1_compile_graph()
    response = part1_stream_graph(graph=graph_part1, user_input=user_input)


    if response:
        return response
    else:
        return "Problems returning data from LLM"
    
@app.route('/api/quick_start/part2', methods= ['POST'])
def api_part2():
    ic("api_part2")
    ic(request)
    ic(request.get_json())
    user_input = request.get_json()['user_input']
    ic(user_input)

    # compile graph
    graph_part2 = part2_compile_graph()

    # use graph with our data
    for event in graph_part2.stream({"messages": [("user", user_input)]}):
        for value in event.values():
            ic(value)
            response = "Assistant:", value["messages"][-1].content
            strMessage = str(response)
            socketio.emit("graph_value", strMessage)

    return "Done"
   
@app.route('/api/quick_start/part3', methods= ['POST'])
def api_part3():
    ic("api_part3")
    ic(request)
    ic(request.get_json())
    user_input = request.get_json()['user_input']
    ic(user_input)

    # compile graph
    graph_part3 = part3_compile_graph()

    config = {"configurable": {"thread_id": "1"}}

    # The config is the **second positional argument** to stream() or invoke()!

    if graph_part3 is not None:
        events = graph_part3.stream(
            {"messages": [("user", user_input)]}, config, stream_mode="values"
        )
        for event in events:
            strMessageEvent = str(event)
            resp = event["messages"][-1].content
            socketio.emit("graph_part3", strMessageEvent)
    else:
        ic("we don't have graph_part3")

    return "Done"

@app.route('/api/quick_start/part4', methods= ['POST'])
def api_part4():
    ic("api_part4")
    ic(request)
    ic(request.get_json())
    user_input = request.get_json()['user_input']
    ic(user_input)

    # compile graph
    

    config = {"configurable": {"thread_id": "1"}}

    # The config is the **second positional argument** to stream() or invoke()!

    if graph_part4 is not None:
        events = graph_part4.stream(
            {"messages": [("user", user_input)]}, config, stream_mode="values"
        )
        for event in events:
            if "messages" in event:
                ic(event)
                message = event["messages"][-1]
                socketio.emit("graph_part4", str(message))
        
        snapshot = graph_part4.get_state(config)


        ic(snapshot.next)
        ic(snapshot.next[0])

        next = snapshot.next[0]
        ic(next)


        if next=="tools":
            return "tools"

        '''
        existing_message = snapshot.values["messages"][-1]
        ic(existing_message.tool_calls)
        '''

    else:
        ic("we don't have graph_part4")

    return "Done"

# trying to implement variant with a class
@app.route('/api/quick_start/part5_1', methods= ['POST'])
def api_part5_1():
    ic("api_part5_1")

    user_input = request.get_json()['user_input']
    ic(user_input)

    config = {"configurable": {"thread_id": "1"}}

    graphPart5.stream(user_input=user_input, config=config)


    snapshot = graphPart5.graph.get_state(config=config)
    ic(snapshot)
    ic(snapshot.next)

    existing_message = snapshot.values["messages"][-1]
    ic(existing_message)

    return "OK - p1"
    

#updateState
@app.route('/api/quick_start/part5_2', methods= ['POST'])
def api_part5_2():
    ic("api_part5_2")

    user_input = request.get_json()['user_input']
    ic(user_input)
    config = {"configurable": {"thread_id": "1"}}

    snapshot = graphPart5.graph.get_state(config=config)
    existing_message = snapshot.values["messages"][-1]
    ic("before ne messages")
    ic(existing_message)



    answer = user_input

    new_messages = [
        # The LLM API expects some ToolMessage to match its tool call. We'll satisfy that here.
        ToolMessage(content=answer, tool_call_id=existing_message.tool_calls[0]["id"]),
        # And then directly "put words in the LLM's mouth" by populating its response.
        AIMessage(content=answer),
    ]

    ic(new_messages[-1])

    graphPart5.updateGraphState(config=config, new_messages=new_messages)

    snapshot = graphPart5.getSnapshot(config=config)
        
    # ic(snapshot)
    ic(snapshot.next)

    last2messages = snapshot.values["messages"][-2]
    ic(last2messages)

    return "OK - p2"


#test api call with 2 params
@app.route('/api/quick_start/part5_3', methods= ['POST'])
def api_part5_3():
    ic("api_part5_3")

    user_input = request.get_json()['user_input']
    part = request.get_json()['part']

    ic(user_input)
    ic(part)


    if part == "part1":
        ic("here code for part==part1")
    else:
        ic("here code for part==part2")

    resp = f"api was called with {part}"
    return resp




#bootstrap
@app.route("/bootstrap/bootstrap")
def bootstrap():
    return render_template('bootstrap/bootstrap.html')


# extend test - info
@app.route("/bootstrap/info")
def info():
    return render_template('bootstrap/info.html')

# extend test - info
@app.route("/bootstrap/test_ext")
def test_ext():
    return render_template('bootstrap/test_ext.html')


# test sumbitting a form data
@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
    if request.method == 'POST':
        # This is where you'll invoke your function
        ic("we are in post block")
        ic(request)

        value = request.form.get('exampleFormControlInput1')
        ic(request)
        ic(value)
    return render_template('index.html', name = value)


@app.route('/submit_form_part7', methods=['POST', 'GET'])
def submit_form_part7():
    ic("def submit_form_part7")

    if request.method == 'POST':
        # This is where you'll invoke your function
        ic("we are in post block")


        users_input = request.form.get('exampleFormControlInput7')

        ic(users_input)

        graph = graphPart7.graph
        config = {"configurable": {"thread_id": "1"}}

        events = graph.stream(
            {
                "messages": [
                    ("user", users_input)
                ]
            },
            config,
            stream_mode="values",
    )
    for event in events:
        if "messages" in event:
            ic(event["messages"][-1])




    return render_template('index.html')



    
@app.route('/api/playground', methods= ['POST'])
def api_playground():
    ic("api_playground")
    ic(request)
    ic(request.get_json())
    user_input = request.get_json()['user_input']
    ic(user_input)

    squares = square_numbers()

    # Print the squares
    for square in squares:
        ic(square)
        socketio.emit('square', square)
   
    return "OK"
    
### end routes


# listeners
@socketio.on('part4_proceed')
def part4_proceed(data):
    ic("part4_proceed: " + str(data))
    config = {"configurable": {"thread_id": "1"}}
    proceedWithNone(graph=graph_part4, config=config)

### end listeners


# endregion

if __name__ == '__main__':
    socketio.run(app, debug=True, use_reloader=True)