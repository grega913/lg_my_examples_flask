# LangGraph Tutorials and HowTos with Flask.

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
