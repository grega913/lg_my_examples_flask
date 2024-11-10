from flask import Flask, url_for, request, render_template, jsonify, session
from flask_session import Session
from flask_socketio import SocketIO
from flask_caching import Cache

from icecream import ic
import time
import sys
import os

from langchain_core.messages import AIMessage, ToolMessage

from tutorials.helperz_tutorials import stream_graph_updates, proceedWithNone
from tutorials.quick_start.part1 import part1_compile_graph, part1_stream_graph, GraphPart1
from tutorials.quick_start.part2 import part2_compile_graph
from tutorials.quick_start.part3 import part3_compile_graph
from tutorials.quick_start.part4 import part4_compile_graph
from tutorials.quick_start.part5 import GraphPart5
from tutorials.quick_start.part7 import GraphPart7

from playground.playground import square_numbers

from al_cohort.lesson8.l8_helperz import get_user_data, OnboardingAssistant_2, appendMessageToSessionMessages
from al_cohort.lesson8.l8_prompts import SYSTEM_PROMPT,WELCOME_MESSAGE
from langchain_groq import ChatGroq

llm = ChatGroq(model="llama-3.1-8b-instant")

dir_path = os.path.dirname(os.path.abspath(__file__))
vectorstore_path = os.path.join(dir_path, "al_cohort", "lesson8", "vectorstore")
policy_file_path = os.path.join(dir_path, "al_cohort", "lesson8", "data", "umbrella_corp_policies.pdf")



ic(vectorstore_path)
ic(policy_file_path)

onboardingAssistant = None

# defining app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'veryStrogSecrekKey'

socketio = SocketIO(app)

# add session support
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

''' initializing some variables, will make them global in "before_route and access them in route'''
mock_user = get_user_data()
graphPart1 = None # we'll defined it in before_request as a global variable and then use it in a route



# graph_part4 = part4_compile_graph()


# graph as Class
''' turn off for development
graphPart5 = GraphPart5()
graphPart7 = GraphPart7()

'''



# this is the function performed before request is made - we can use it to do some jobs before request is made
@app.before_request
def before_request():
    ic(f"def before request and request is {request}")
    global graphPart1
    

    if request.path == '/lg_tutorials/quick_start/part1_2':
        if graphPart1 is None:
            graphPart1 = GraphPart1()
            graphPart1.compile_graph()
            ic(graphPart1)
    if request.path == '/lg_tutorials/quick_start/part2_2':
        global graphPart2
        if graphPart2 is None:
            graphPart2 = GraphPart1()
            graphPart2.compile_graph()
            ic(graphPart2)






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

@app.route('/lg_tutorials/quick_start/<path:path>', methods = ['GET', 'POST'])
def quick_start(path):

    if not 'messages' in session:
        session["messages"] = []

    if path =="part1":
        return render_template('quick_start/part1.html')
    elif path == "part1_2":

        response = ""

        if request.method == 'POST':
            # This is where you'll invoke your function
            ic("we are in post block in part1_2")
            users_input = request.form.get('input_field_graphPart1')
            ic(users_input)
                        
            if graphPart1 is not None and users_input != "":
                ic(f"should be sending to get_stream users_input: {users_input} ")
                resp = graphPart1.stream(user_input=users_input)

                appendMessageToSessionMessages(role = "user", message=users_input, session=session)
                appendMessageToSessionMessages(role="ai", message=resp, session = session)

            return render_template('quick_start/part1_2.html', user = mock_user, messages = session['messages'])
    
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



'''
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

        
        existing_message = snapshot.values["messages"][-1]
        ic(existing_message.tool_calls)
        

    else:
        ic("we don't have graph_part4")

    return "Done"

    
'''


'''
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

    
    '''


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


#
@app.route("/bootstrap/info_2")
def info_2():
    return render_template('bootstrap/base_2.html')

# example of template with collapsable sidebar
@app.route("/bootstrap/boot_play")
def boot_play():
    return render_template('bootstrap/boot_play.html')


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


@app.route('/submit_form_mock', methods=['POST', 'GET'])
def submit_form_mock():
    if request.method == 'POST':
        # This is where you'll invoke your function
        ic("we are in post block of def submit_form_rock")
        ic(request)

        value = request.form.get('submit_form_mock')
        ic(request)
        ic(value)
    return render_template('quick_start/part1_2.html', user = mock_user)

'''
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


'''
    
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





# region Alejandro's Cohort

# before/outside the route we initilaze stuff that only needs to be done once
# and should not be repeated with every call
# values for user and messages will be store in session, and therefore should be initialized within route

# lesson 8


# vector_store = init_vector_store_2(pdf_path=policy_file_path, persistent_path=vectorstore_path)

'''
onboardingAssistant = OnboardingAssistant_2(
    system_prompt = SYSTEM_PROMPT,
    llm=llm,
    persist_directory=vectorstore_path,
    session = session
)
'''



def quick_start_part_1_2():

    num = 0

    if graphPart1 is not None:
        graphPart1.stream
    else:
        ic(" we do not have graphPart1 in route")
        pass


    return num




# this is the route for lesson8 - 
@app.route("/al_cohort/lesson8", methods= ['POST', 'GET'])
def lesson8():
    ic("def lesson8 in route")

    users_input = ""


    # check to see if we have user in session and create one iof none
    if not 'user' in session:
        session["user"] = get_user_data()

    # check to see if we have messages in session and init some of not
    if not 'messages' in session:
        session["messages"] = []
    
    if not "calls" in session:
        session["calls"] = 0
    
    session["calls"] = session["calls"] + 1

    # this part gets executed after the submit button is clicked in lesson8.html
    if request.method == 'POST':
        # This is where you'll invoke your function
        ic("we are in post block in lesson8")

        users_input = request.form.get('input_field_lesson8')
        last_message = users_input
        
    
    if users_input != "":
        response_generator = onboardingAssistant.get_response(user_input=users_input, session = session)
        str_tot = ""

        # because get_response returns a stream on chain, we need to combine it
        for ckunk in response_generator:
            str_tot = str_tot + str(ckunk)

        appendMessageToSessionMessages(role = "user", message=users_input, session=session)
        appendMessageToSessionMessages(role="ai", message=str_tot, session = session)

    return render_template('al_cohort/lesson8.html', user=session["user"], messages = session["messages"])


# endregion







if __name__ == '__main__':



    socketio.run(app, debug=True, use_reloader=True)