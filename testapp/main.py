from flask import Flask


app = Flask(__name__)

@app.route("/")
def home():
    return "hello world!"


def run_app(first, second):
    # app.run(host='0.0.0.0', port=5000)
    return app