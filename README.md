# LangGraph Tutorials and HowTos with Flask, Bootstrap.

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
