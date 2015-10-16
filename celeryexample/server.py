from flask import Flask, jsonify

from celeryexample import tasks

app = Flask(__name__)

@app.route('/')
def index():
    result = tasks.add_one.delay(1)
    return jsonify(id=result.id)

if __name__ == '__main__':
    app.run()


