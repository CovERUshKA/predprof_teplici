import threading
import collector
import database as db

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

# http://127.0.0.1:80/api/v1/sensors_data?time_period=<time_in_seconds>
@app.route('/api/v1/sensors_data')
def sensors_data():
    arguments = request.args

    time_period = arguments.get("time_period", None, type=int)

    if time_period == None:
        return ErrorResponse("No time_period provided or it is incorrect", 400)

    air, ground = db.get_all_data(time_period)

    ret = {
        "air": air,
        "ground": ground
    }

    return SuccessResponse(ret)

@app.route('/')
def index():
    return "Hello, World!"

if __name__ == '__main__':

    t = threading.Thread(target=collector.infinite_collect)
    t.start()

    app.run(debug=False,  port=80, host="0.0.0.0")

    print("flask ended")

    collector.end_working = True
