import threading
import collector

from flask import Flask, jsonify, request

app = Flask(__name__)

def SuccessResponse(result):
    response = {"ok":True, "result":result}

    return jsonify(response)

#{
#   ok: false,
#   error_code: error_code,
#   description: "wewewe"
# }
def ErrorResponse(description, error_code):
    response = {"ok":False, "error_code":error_code, "description":description}

    return jsonify(response), error_code

@app.route('/')
def index():
    return "Hello, World!"

if __name__ == '__main__':

    t = threading.Thread(target=collector.infinite_collect)
    t.start()

    app.run(debug=False,  port=80, host="0.0.0.0")
