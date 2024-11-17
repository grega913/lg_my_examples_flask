from flask import Flask, url_for, request, render_template, jsonify, session, redirect
from flask_session import Session
from flask_socketio import SocketIO
from flask_caching import Cache

import logging

from icecream import ic
import time
import sys
import os

from langchain_core.messages import AIMessage, ToolMessage

from tutorials.helperz_tutorials import stream_graph_updates, proceedWithNone, createRandomString,extract_messages_from_snapshot, detect_message_type, check_snapshot_next, routingInPart4_2, check_snapshot_next_human
from tutorials.quick_start.part1 import part1_compile_graph, part1_stream_graph, GraphPart1
from tutorials.quick_start.part2 import part2_compile_graph, GraphPart2
from tutorials.quick_start.part3 import part3_compile_graph, GraphPart3
from tutorials.quick_start.part4 import part4_compile_graph, GraphPart4
from tutorials.quick_start.part5 import GraphPart5, GraphPart5_2
from tutorials.quick_start.part7 import GraphPart7
from tutorials.quick_start.part6 import GraphPart6_2


from playground.playground import square_numbers, generate_random_string, get_summaryFromSnapshot, get_messagesFromSnapshot

from al_cohort.lesson8.l8_helperz import get_user_data, OnboardingAssistant_2, appendMessageToSessionMessages, appendSummaryToSessionMessages
from al_cohort.lesson8.l8_prompts import SYSTEM_PROMPT,WELCOME_MESSAGE
from al_cohort.lesson11.l11 import GraphLesson11, GraphLesson11_MultipleTools
from al_cohort.lesson12.l12 import GraphLesson12_1, GraphLesson12_2

from langchain_groq import ChatGroq

llm = ChatGroq(model="llama-3.1-8b-instant")

dir_path = os.path.dirname(os.path.abspath(__file__))
vectorstore_path = os.path.join(dir_path, "al_cohort", "lesson8", "vectorstore")
policy_file_path = os.path.join(dir_path, "al_cohort", "lesson8", "data", "umbrella_corp_policies.pdf")


# ic(vectorstore_path)
# ic(policy_file_path)

onboardingAssistant = None

# defining app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'veryStrongSecrekKey'

logging.getLogger("werkzeug").disabled = True
logging.getLogger("geventwebsocket.handler").disabled = True


socketio = SocketIO(app)

# add session support
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

''' initializing some variables, will make them global in "before_route and access them in route'''

graphPart1 = None # we'll defined it in before_request as a global variable and then use it in a route
graphPart2 = None
graphPart3 = None
graphPart4 = None
graphPart5 = None
graphPart6 = None
graphLesson11 = None
graphLesson11_withToolNode = None
graphLesson11_multiple_tools = None
graphLesson12_1 = None
graphLesson12_2 = None





# graph_part4 = part4_compile_graph()


# graph as Class
''' turn off for development
graphPart5 = GraphPart5()
graphPart7 = GraphPart7()

'''


# this is the function performed before request is made - we can use it to do some jobs before request is made
@app.before_request
def before_request():
    #ic(f" - - - - - - - - - - - - - - - def before request and request is ${request}")
    

    if 'user' not in session:
        session['user'] = get_user_data()
    


    if request.path == '/lg_tutorials/quick_start/part1_2':
        global graphPart1
        if graphPart1 is None:
            graphPart1 = GraphPart1()
            graphPart1.compile_graph()
            ic(graphPart1)
    if request.path == '/lg_tutorials/quick_start/part2_2':
        global graphPart2
        if graphPart2 is None:
            graphPart2 = GraphPart2()
            graphPart2.compile_graph()
            ic(graphPart2)
    if request.path == '/lg_tutorials/quick_start/part3_2':
        global graphPart3
        if graphPart3 is None:
            if not 'threadId' in session:
                ic("we do not havev threadId in session, will create one")
                session['threadId'] = createRandomString()
            
            graphPart3 = GraphPart3(session['threadId'])

            graphPart3.compile_graph()
            ic(graphPart3)
    if request.path == '/lg_tutorials/quick_start/part4_2':
        global graphPart4
        
        # human in the loop
        if graphPart4 is None:
            graphPart4 = GraphPart4(threadId="3")
            # compiled graph with interrupt before
            graphPart4.compile_graph_with_interrupt_before()
            if 'messages' not in session:
                session['messages'] = []
    
            if 'messages' in session:
                session['messages']= []
    if request.path == '/lg_tutorials/quick_start/part5_2':
        global graphPart5
        if graphPart5 is None:
            graphPart5 = GraphPart5_2(threadId="5")
            # compiled graph with interrupt before
            graphPart5.compile_graph_with_interrupt_before()
            if 'messages' not in session:
                session['messages'] = []

            if 'messages' in session:
                session['messages']= []
    if request.path == '/lg_tutorials/quick_start/part6_2':
        global graphPart6
        if graphPart6 is None:
            graphPart6 = GraphPart6_2(threadId="6")
            # compiled graph with interrupt before
            graphPart6.compile_graph()

            if 'messages' not in session:
                session['messages'] = []
    
            if 'messages' in session:
                session['messages']= []
    if request.path == '/al_cohort/lesson11':
        global graphLesson11
        global graphLesson11_withToolNode
        if graphLesson11 is None:
            graphLesson11 = GraphLesson11(threadId="l11")
            graphLesson11.compile_graph()
            if 'messages' not in session:
                session['messages'] = []
    
            if 'messages' in session:
                session['messages']= []
    if request.path == '/al_cohort/lesson11_mt':
        global graphLesson11_multiple_tools
        if graphLesson11_multiple_tools is None:
            graphLesson11_multiple_tools = GraphLesson11_MultipleTools(threadId="l11")
            graphLesson11_multiple_tools.compile_graph_multiple_tools()

            if 'messages' not in session:
                session['messages'] = []
    
            if 'messages' in session:
                session['messages']= []
    if request.path == '/al_cohort/lesson12_1':
        global graphLesson12_1
        if graphLesson12_1 is None:
            graphLesson12_1 = GraphLesson12_1(threadId="12_1")
            graphLesson12_1.compile_graph()

            if 'messages' not in session:
                session['messages'] = []
    
            if 'messages' in session:
                session['messages']= []
    if request.path == '/al_cohort/lesson12_2':
        global graphLesson12_2
        if graphLesson12_2 is None:
            random_string = generate_random_string(5)
            ic(random_string)
            graphLesson12_2 = GraphLesson12_2(threadId=random_string)
            graphLesson12_2.compile_graphLesson12_2()

            ic(graphLesson12_2)

            if 'messages' not in session:
                session['messages'] = []
    
            if 'messages' in session:
                session['messages']= []

# region TutorialsRoutes
@app.route('/index')
def index(name="Default Name"):
    return render_template('index.html', name=name)

@app.route('/about')
def about():
    return render_template('about.html')



@app.route("/playground", methods= ['GET', 'POST'])
def playground():
    if request.method == 'POST':
        time.sleep(5)
        return render_template('playground.html', message="Function executed!")
    else:
        ic("else")
    return render_template('playground.html')


# this is main route for quick_start tutorial
# it serves all parts, from part1 to part6
@app.route('/lg_tutorials/quick_start/<path:path>', methods = ['GET'])
def quick_start(path):
    ic(f"quick_start, path: ${path}, request_method: ${request.method}")
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
    
    elif path == "part2_2":
        events_count = 0
        events = []

        if request.method == 'POST':
            # This is where you'll invoke your function
            ic("we are in post block in part1_2")
            user_input = request.form.get('input_field_graphPart2')
            ic(user_input)
                        
            if graphPart2 is not None and user_input != "":
                ic(f"should be sending to get_stream users_input: {user_input}")

                for event in graphPart2.graph.stream({"messages": [("user", user_input)]}):
                    events.append(event)
                    events_count +=1
                    ic(events_count)
                    time.sleep(1)
                    ic(event)

                
            
            appendMessageToSessionMessages(role = "user", message=user_input, session=session)
            #appendMessageToSessionMessages(role="ai", message=resp, session = session)

            return render_template('quick_start/part2_2.html', user = mock_user, messages=session['messages'])

    elif path == "part3":
        return render_template('quick_start/part3.html')
    elif path == "part3_2":
        ic("we are in path3_2 now")


        
        if request.method == 'POST':
            users_input=""
            ic("we are in post block in part3_2")

            users_input = request.form.get('input_field_graphPart3')
        
            



                        
            if graphPart3 is not None and users_input != "":
                ic(f"should be sending to getStream users_input: {users_input}")

                events = graphPart3.getStream(user_input=users_input)
                
                for event in events:
                    ic(event["messages"][-1])

                    last_message = event['messages'][-1]

                    last_message = detect_message_type(last_message)

                    if (last_message["role"] !="" and last_message["content"] !=""):
                        ic("we have role and content and will update messages in session now")
                        appendMessageToSessionMessages(role = last_message["role"], message=last_message["content"], session = session)
                    
                    ic(" - - - - - - - - - - - - - - - ")

               

                return redirect( url_for('quick_start', path = "part3_2"))

             
        return render_template('quick_start/part3_2.html', user = mock_user, messages = session['messages'])

    elif path == "part4":
        return render_template('quick_start/part4.html')
    
    elif path=="part4_2":
        ic("def path==part4_2, just before render_template")
        err = request.args.get('err', '')
        displayBtnProceed = request.args.get('displayBtnProceed', False)

        ic(err)
        ic(displayBtnProceed)

        return render_template('quick_start/part4_2.html', user = session['user'], messages = session['messages'], err = err, displayBtnProceed = displayBtnProceed)

    elif path == "part5":

        return render_template('quick_start/part5.html')
    
    elif path =="part5_2":
        ic("def path==part5_2, just before render_template")
        err = request.args.get('err', '')
        displayBtnProceed = request.args.get('displayBtnProceed', False)

        ic(err)
        ic(displayBtnProceed)

        return render_template('quick_start/part5_2.html', user = session['user'], messages = session['messages'], err = err, displayBtnProceed = displayBtnProceed)
    
    elif path == "part6":
        return render_template('quick_start/part6.html')
    elif path == "part6_2":
        ic("in path part6_2")
        err=None
        displayBtnProceed=None
        return render_template('quick_start/part6_2.html', user = session['user'], messages = session['messages'], err = err, displayBtnProceed = displayBtnProceed)
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

# this is called at begginning in part4_2
@app.route('/api/quick_start/part4_2', methods= ['POST'])
def api_part4_2():
    ic("def api_part4_2 - stage 1")

    displayBtnProceed = False # checker for displaying a button in a template

    try:
        users_input = request.form.get('input_field_graphPart4')
        ic(users_input)
        if not users_input:
            raise ValueError("Input field is empty")
        if not graphPart4:
            raise ValueError("graphPart4 is not defined in /api/quick_start/part4_2")
        events_generator = graphPart4.getStream(user_input=users_input)
        for event in events_generator:
            if "messages" in event:
                event["messages"][-1].pretty_print()
        snapshot = graphPart4.getSnapshot()

        messages = extract_messages_from_snapshot(snapshot=snapshot)
        ic(messages)

        session['messages'] = []

        for message in messages:
            
            messageToAppend = detect_message_type(message)
            appendMessageToSessionMessages(role = messageToAppend["role"], message = messageToAppend['content'], session = session,)
            ic(messageToAppend)


        # here we are checking if snapshot.next == ('tools')
        displayBtnProceed = check_snapshot_next(snapshot=snapshot)
        ic(displayBtnProceed)

        if displayBtnProceed:
            ic("displayBtnProceed is true and we should send this param")
            return redirect(url_for('quick_start', path = "part4_2", messages = session['messages'], displayBtnProceed = displayBtnProceed))

        return redirect(url_for('quick_start', path = "part4_2", messages = session['messages']))
    
    except Exception as e:
        return redirect(url_for('quick_start', path = "part4_2", err=e))
    finally:

        ic("finally in post route part4_2")

#this is called when the user clicks PROCEED To TOOLS
@app.route('/api/quick_start/part4_2_proceed', methods= ['POST'])
def api_part4_2_proceed():
    ic("def api_part4_2_proceed - stage 2")

    displayBtnProceed = False # checker for displaying a button in a template

    try:
        users_input = request.form.get('input_field_graphPart4')
        ic(users_input)
        if not graphPart4:
            raise ValueError("graphPart4 is not defined in /api/quick_start/part4_2_proceed")
        
        events_generator = graphPart4.getStreamWithNone()
        for event in events_generator:
            if "messages" in event:
                message = event["messages"][-1].pretty_print()

        session['messages'] = []        
        snapshot = graphPart4.getSnapshot()
        messages = extract_messages_from_snapshot(snapshot=snapshot)
        ic(messages)
        for message in messages:
            
            messageToAppend = detect_message_type(message)
            appendMessageToSessionMessages(role = messageToAppend["role"], message = messageToAppend['content'], session = session)
            ic(messageToAppend)


        return redirect(url_for('quick_start', path = "part4_2", messages = session['messages']))
    
    except Exception as e:
        return redirect(url_for('quick_start', path = "part4_2", messages = session['messages'], err=e))
    finally:

        ic("finally in post route part4_2 - stage 2")

# this is called at begginning in part5_2
@app.route('/api/quick_start/part5_2', methods= ['POST'])
def api_part5_2():
        ic("def api_part5_2 - stage 1")

        displayBtnProceed = False # checker for displaying a button in a template

        try:
            users_input = request.form.get('input_field_graphPart5')
            ic(users_input)
            if not users_input:
                raise ValueError("Input field is empty")
            if not graphPart5:
                raise ValueError("graphPart5 is not defined in /api/quick_start/part5_2")
            events_generator = graphPart5.getStream(user_input=users_input)
            for event in events_generator:
                if "messages" in event:
                    event["messages"][-1].pretty_print()

            snapshot = graphPart5.getSnapshot()
            ic(snapshot)
            ic(snapshot.next)

            time.sleep(3)

            messages = extract_messages_from_snapshot(snapshot=snapshot)
            ic(messages)

            session['messages'] = []
            for message in messages:
                messageToAppend = detect_message_type(message)
                appendMessageToSessionMessages(role = messageToAppend["role"], message = messageToAppend['content'], session = session,)
                ic(messageToAppend)


            # here we are checking if snapshot.next == ('tools')
            displayBtnProceed = check_snapshot_next(snapshot=snapshot)
            ic(displayBtnProceed)

            if displayBtnProceed:
                ic("displayBtnProceed is true and we should send this param")
                return redirect(url_for('quick_start', path = "part5_2", messages = session['messages'], displayBtnProceed = displayBtnProceed))

            return redirect(url_for('quick_start', path = "part5_2", messages = session['messages']))
        
        except Exception as e:
            return redirect(url_for('quick_start', path = "part5_2", err=e))
        finally:
            ic("finally in post route part5_2")


'''this is called in the second stage in Part5_2
user is provided with 2 options:
1. Proceed with using the tool - by clicking a button PROCEED TO TOOLS
2. Writing his/her own answer in case he thinks tool calling is not necessary
'''
@app.route('/api/quick_start/part5_2_proceed', methods= ['POST'])
def api_part5_2_proceed():
    ic("def api_part5_2_proceed - stage 2")


    e=None
    answer = None
    ic(request.form)
    displayBtnProceed = False # checker for displaying a button in a template
    step = request.form.get('step') # this is defined in form that is calling a function
    ic(step)

    answer = request.form.get("answer") # here we check if we have response
    ic(answer)


    if answer and answer !="":
        ic(f"user provided an answer, we should not call tools: ${answer}")
        snapshot = graphPart5.getSnapshot()
        existing_message = snapshot.values["messages"][-1]
        existing_message.pretty_print()

        new_messages = [
        # The LLM API expects some ToolMessage to match its tool call. We'll satisfy that here.
        ToolMessage(content=answer, tool_call_id=existing_message.tool_calls[0]["id"]),
        # And then directly "put words in the LLM's mouth" by populating its response.
        AIMessage(content=answer),
        ]

        new_messages[-1].pretty_print()

        
        # updating state with user's message
        snapshot = graphPart5.updateState(new_messages)
        ic(snapshot.values["messages"][-2:])
        

        '''option where we are updating state at defined node
        we can basically push user's message into chatbot, so that it appears as the ai responded with answer,
        but it is actually user's message
        
        snapshot = graphPart5.updateStateWithNodeDefined(
            messages= [AIMessage(content=answer)],
            as_node="chatbot"
        )
        ic(snapshot.values["messages"][-3:])
        '''

        session['messages'] = [] 
        messages = extract_messages_from_snapshot(snapshot=snapshot)
        for message in messages:
    
            messageToAppend = detect_message_type(message)
            appendMessageToSessionMessages(role = messageToAppend["role"], message = messageToAppend['content'], session = session)
            ic(messageToAppend)



        

    else:
        ic(f"user wants to execute tool call-> we should proceed with streamWithNone")
        try:
            #users_input = request.form.get('input_field_graphPart5')
            #ic(users_input)

            if not graphPart5:
                raise ValueError("graphPart5 is not defined in /api/quick_start/part5_2_proceed")
            
            events_generator = graphPart5.getStreamWithNone()
            for event in events_generator:
                if "messages" in event:
                    message = event["messages"][-1].pretty_print()

            session['messages'] = []        
            snapshot = graphPart5.getSnapshot()
            messages = extract_messages_from_snapshot(snapshot=snapshot)
            ic(messages)
            for message in messages:
                
                messageToAppend = detect_message_type(message)
                appendMessageToSessionMessages(role = messageToAppend["role"], message = messageToAppend['content'], session = session)
                ic(messageToAppend)


            #return redirect(url_for('quick_start', path = "part5_2", messages = session['messages']))
    
        except Exception as e:
            return redirect(url_for('quick_start', path = "part5_2", messages = session['messages'], err=e))
        finally:

            ic("finally in post route part4_2 - stage 2")
    
    return redirect(url_for('quick_start', path = "part5_2", messages = session['messages'], err=e)) 
    

@app.route('/api/quick_start/part6_2', methods= ['POST'])
def api_part6_2():
    ic("api_part6_2")
    e=None
    snapshotNextIsHuman=None
    try:
        users_input = request.form.get('input_field_graphPart6')
        ic(users_input)
        if not users_input:
            raise ValueError("Input field is empty")
        if not graphPart6:
            raise ValueError("graphPart6 is not defined in /api/quick_start/part6_2")
        events_generator = graphPart6.getStream(user_input=users_input)

        for event in events_generator:
            if "messages" in event:
                event["messages"][-1].pretty_print()

        snapshot = graphPart6.getSnapshot()
        ic(snapshot)
        ic(snapshot.next)
        messages = extract_messages_from_snapshot(snapshot=snapshot)
        ic(messages)

        # display messages in web page
        session['messages'] = []
        for message in messages:
            messageToAppend = detect_message_type(message)
            appendMessageToSessionMessages(role = messageToAppend["role"], message = messageToAppend['content'], session = session,)
            ic(messageToAppend)

        # check if snapshot.next == human
        snapshotNextIsHuman = check_snapshot_next_human(snapshot=snapshot)
        ic(snapshotNextIsHuman)
        time.sleep(5)

        if snapshotNextIsHuman:
            ic(snapshotNextIsHuman)

            ai_message = snapshot.values["messages"][-1]
            ic(ai_message)
            time.sleep(3)
            
            human_response = (
                "We, the experts are here to help! We'd recommend you check out LangGraph to build your agent."
                " It's much more reliable and extensible than simple autonomous agents."
            )

            tool_message = graphPart6.create_response(human_response, ai_message)
            ic(tool_message)


            snapshot  = graphPart6.updateState({"messages": [tool_message]})
            ic(" - - - - sad ce snapshot - - - - ")
            ic(snapshot)
            events_generator = graphPart6.getStreamWithNone()
            
            snapshot = graphPart6.getSnapshot()

            ic(snapshot)

            for event in events_generator:
                if "messages" in event:
                    event["messages"][-1].pretty_print()
            
            '''
            snapshot = graphPart6.getSnapshot()

            messages = extract_messages_from_snapshot(snapshot=snapshot)
            ic(messages)
            time.sleep(5)
            # display messages in web page
            session['messages'] = []
            for message in messages:
                messageToAppend = detect_message_type(message)
                appendMessageToSessionMessages(role = messageToAppend["role"], message = messageToAppend['content'], session = session,)
                ic(messageToAppend)
            '''
        






        






        return redirect(url_for('quick_start', path = "part6_2", messages = session['messages']))
    except Exception as e:
        return redirect(url_for('quick_start', path = "part6_2", err=e))
    finally:
        ic("finally in post route part6_2")



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

# endregion


# region bootstrap
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
    
### endregion


# listeners
@socketio.on('part4_proceed')
def part4_proceed(data):
    ic("part4_proceed: " + str(data))
    config = {"configurable": {"thread_id": "1"}}
    proceedWithNone(graph=graph_part4, config=config)

### end listeners


# endregion


# region extras



@app.route('/cleanSessionData', methods = ['GET'])
def cleanSessionData():
    ic("def cleanSessionData")

    ic(request.method)

    if request.method == 'GET':
        ic("we are in post")
        session.clear()
        ic("after session.clear()")

    return redirect(request.referrer)
    


@app.route('/loading_route', methods=['GET', 'POST'])
def your_view_function():
    # Your code here
    if request.method == 'POST':
        # Start the loading indicator
        return render_template('index.html', loading=True)
    else:
        # Stop the loading indicator
        return render_template('index.html', loading=False)


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



@app.route("/al_cohort/lesson11", methods= ['GET'])
def lesson11():
    ic("route lesson11")

    if not "messages" in session:
        session["messages"] = []

    return render_template('al_cohort/lesson11.html', messages = session['messages'])




@app.route('/api/lesson11', methods= ['POST'])
def api_lesson11():
        ic("def api_lesson11")


        try:
            users_input = request.form.get('lesson11')
            ic(users_input)

            if not users_input:
                raise ValueError("Input field is empty")
            if not graphLesson11:
                raise ValueError("graph is not defined in /api/lesson11")
            
            time.sleep(5)
            response = graphLesson11.invokeGraph11(message = users_input)
            ic(response)

            for m in response['messages']:
                message = detect_message_type(m)
                appendMessageToSessionMessages(role=message["role"], message=message["content"], session=session)
                ic(message)
            
            ic("session[messages]")
            ic(session["messages"])            



            return redirect(url_for('lesson11', messages = session['messages']))
        
        except Exception as e:
            return redirect(url_for('lesson11', err=e))
        finally:
            ic("finally in post route lesson11")


@app.route("/al_cohort/lesson11_mt", methods= ['GET'])
def lesson11_mt():
    ic("route lesson11_mt")
    if not "messages" in session:
        session["messages"] = []
    return render_template('al_cohort/lesson11_mt.html', messages = session['messages'])



@app.route('/api/lesson11_mt', methods= ['POST'])
def api_lesson11_mt():
        ic("def api_lesson11_mt")
        try:
            users_input = request.form.get('lesson11_mt')
            ic(users_input)

            if not users_input:
                raise ValueError("Input field is empty")
            if not graphLesson11_multiple_tools:
                raise ValueError("graph is not defined in /api/lesson11")
               
            response = graphLesson11_multiple_tools.invokeGraph11_multiple_tools(message = users_input)
            ic(response)

            for m in response['messages']:
                message = detect_message_type(m)
                appendMessageToSessionMessages(role=message["role"], message=message["content"], session=session)
                ic(message)
            
            ic("session[messages]")
            ic(session["messages"])            


            return redirect(url_for('lesson11_mt', messages = session['messages']))
        
        except Exception as e:
            return redirect(url_for('lesson11_mt', err=e))
        finally:
            ic("finally in post route lesson11_mt")


@app.route("/al_cohort/lesson12_1", methods= ['GET'])
def lesson12_1():
    ic("route lesson12_1")
    if not "messages" in session:
        session["messages"] = []
    return render_template('al_cohort/lesson12_1.html', messages = session['messages'])


@app.route('/api/lesson12_1', methods= ['POST'])
def api_lesson12_1():
        ic("def api_lesson12_1")
        try:
            users_input = request.form.get('lesson12_1')
            ic(users_input)

            if not users_input:
                raise ValueError("Input field is empty")
            if not graphLesson12_1:
                raise ValueError("graph is not defined in /api/lesson12_1")
               
            response = graphLesson12_1.invokeGraph12(message = users_input)
            ic(response)

            for m in response['messages']:
                message = detect_message_type(m)
                appendMessageToSessionMessages(role=message["role"], message=message["content"], session=session)
                ic(message)
            
            ic("session[messages]")
            ic(session["messages"])            


            return redirect(url_for('lesson12_1', messages = session['messages']))
        
        except Exception as e:
            return redirect(url_for('lesson12_1', err=e))
        finally:
            ic("finally in post route lesson12_1")





@app.route("/al_cohort/lesson12_2", methods= ['GET'])
def lesson12_2():
    ic("route lesson12_2")
    e=None
    if not "messages" in session:
        session["messages"] = []
    return render_template('al_cohort/lesson12_2.html', messages = session['messages'], err=e)


@app.route('/api/lesson12_2', methods= ['POST'])
def api_lesson12_2():
        ic("def api_lesson12_2")
        try:
            users_input = request.form.get('lesson12_2')
            ic(users_input)

            if not users_input:
                raise ValueError("Input field is empty")
            
            if not graphLesson12_2:
                raise ValueError("graph is not defined in /api/lesson12_2")
               
            response = graphLesson12_2.invokeGraph12_2(message = users_input)
            state = graphLesson12_2.getState()
            #ic(state)

            if "messages" in session:
                session['messages'] = []
            
            messages = state.values.get("messages")
            ic(messages)
            for m in messages:
                message = detect_message_type(m)
                appendMessageToSessionMessages(role=message["role"], message=message["content"], session=session)

            # check if we have summary
            summary = state.values.get("summary")
            ic(summary)
            if summary is not None:
                appendSummaryToSessionMessages(summary = summary, session = session)

            
            


            return redirect(url_for('lesson12_2', messages = session['messages']))
        
        except Exception as e:
            return redirect(url_for('lesson12_2', err=e))
        finally:
            ic("finally in post route lesson12_2")


# endregion


 




if __name__ == '__main__':



    socketio.run(app, debug=False, use_reloader=True, port=5005)