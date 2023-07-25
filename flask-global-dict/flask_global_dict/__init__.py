from functools import wraps

import flask


global_dict = {}


app = flask.Flask(__name__)
 

def some_decorator():
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            global_dict['foo'] = flask.request.args.get('foo', 'bar')
            return f(*args, **kwargs)
        return decorated
    return wrapper

@some_decorator()
def update_global_dict():
    global_dict['bar'] = global_dict['foo']

app.before_request(update_global_dict)

@app.route('/')
def app_main():
    return flask.jsonify(global_dict)
