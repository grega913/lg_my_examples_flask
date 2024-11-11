# LangGraph Tutorials and HowTos with Flask, Bootstrap.

## 20241111 - Quickstart tutorial created differently

1.  Templates are:

    - src/templates/quick_start/part1_2.html
    - src/templates/quick_start/part2_2.html
    - src/templates/quick_start/part3_2.html
    - src/templates/quick_start/part4_2.html
    - src/templates/quick_start/part5_2.html
    - src/templates/quick_start/part6_2.html

    They are all extending base template: - src/templates/quick_start/quick_start_base.html - many elements are macros from src/templates/playground/macros

2.  Classes for Graphs are defined in:

    - src/tutorials/quick_start/part1.py
    - src/tutorials/quick_start/part2.py
    - src/tutorials/quick_start/part3.py
    - src/tutorials/quick_start/part4.py
    - src/tutorials/quick_start/part5.py
    - src/tutorials/quick_start/part6.py

3.  Some data is in session variable, defined in main.py - session['messages'], session ['user']
4.  In code we want to initialize graph classes at right places.Usually this are variables created in @before_route as global variables. We can access them and perform some function within route on subsequent calls.

## 20241109 - Will do QuickStart Tutorial nicely, with base template and macros:

- src/templates/quick_start/quick_start_base_2.html

## 20241109 - Playing with extending templates, macros, ...

- src/templates/quick_start/quick_start_base.html -> base template
- src/templates/quick_start/part1_2.html -> is extending base tempalte
- src/templates/playground/macros -> few macros defined, that are imported into templates

## 20241108 - OnboardingAssistant for Umbrella Corp

OnboardingAssistant added:

- @app.route("/al_cohort/lesson8", methods= ['POST', 'GET'])
- This is the flask version of Alejandro's code from lesson8 - OnboardingAssistant for Umbrella corp.

## 20241021 - Bootstrap

Playing around with Bootsrap. Created 3 routes:

- bootstrap/boostrap -> bootstrap/bootstrap.html
- bootstrap/info -> bootstrap/info.html
- bootstrap/test_ext -> boostrap/test_ext.html

Messing around with extending templates . . from base.html and using macros in base.html

## Main Logic goes like this:

1. Create a route [GET] for rendering template -> main.py All routes are defined here

```
@app.route('/index')
def index():
    return render_template('index.html')
```

2. Prepare html template in 'static/templates ...' Make sure to add elements (could be empty elements, that will be used by js)
3. In header, make sure to correctly import js and css file
4. Prepare js file, in 'static/js folder'. For readibility make a single js file for single html code
5. For api functionality, prepare [POST] routes in main.py file
6. When we stream data from model, use sockets for communication between py and js. Example in playground.

## Some issues when importing functions

- here we find the directory where we have helperz_tutorials.py

'parent_dir_of_helperz_tutorials = os.path.dirname(os.path.dirname(os.path.abspath(**file**)))'

- we append this directory to the sys path

'sys.path.append(parent_dir_of_helperz_tutorials)'

- now we can import function from this file/module

'from helperz_tutorials import stream_graph_updates'
