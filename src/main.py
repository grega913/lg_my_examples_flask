from flask import Flask, redirect, url_for, request, render_template, jsonify
from flask_socketio import SocketIO
from icecream import ic
import time
import sys
import os

from tutorials.helperz_tutorials import stream_graph_updates
from tutorials.quick_start.part1 import part1_compile_graph, part1_stream_graph
from tutorials.quick_start.part2 import part2_compile_graph

from playground.playground import square_numbers


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# region Routes
@app.route('/index')
def index():
    return render_template('index.html')

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

    graph = part1_compile_graph()
    response = part1_stream_graph(graph=graph, user_input=user_input)


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
    graph = part2_compile_graph()

    # use graph with our data
    for event in graph.stream({"messages": [("user", user_input)]}):
        for value in event.values():
            ic(value)
            response = "Assistant:", value["messages"][-1].content
            strMessage = str(response)
            socketio.emit("graph_value", strMessage)

    return "Done"
   

    
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
    





# endregion

if __name__ == '__main__':
    socketio.run(app, debug=True, use_reloader=True)