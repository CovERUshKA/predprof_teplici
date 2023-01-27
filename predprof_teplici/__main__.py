import threading
import collector
import database as db
import asyncio
import time
import requests
import config

from flask import Flask, jsonify, request, abort, make_response, render_template

app = Flask(__name__)

settings = {
    "parameters": {
        "T": None,
        "H": None,
        "Hb": None
    },
    "fork_drive": None,
    "total_hum": None,
    "emergency": 0,
    "watering": [None, None, None, None, None, None]
}

def SuccessResponse(result):
    response_data = {"ok":True, "result":result}
    
    response = make_response(jsonify(response_data))
    
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers["Content-Type"] = "application/json"
    
    return response

#{
#   ok: false,
#   error_code: error_code,
#   description: "wewewe"
#}
def ErrorResponse(description, error_code):
    response_data = {"ok":False, "error_code":error_code, "description":description}

    response = make_response(jsonify(response_data), error_code)

    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers["Content-Type"] = "application/json"

    return response

def check_parameters(data, parameters):
    try:
        assert type(data) == dict, ('data', 404)

        for param in parameters:
            if (param[0] in data) == True:
                assert type(data.get(param[0])) == param[1], (param[0], 400)
            else:
                raise AssertionError((param[0], 404))
    except AssertionError as e:
        abort(ErrorResponse(f"field \"{e.args[0][0]}\" incorrect", e.args[0][1]))

# http://127.0.0.1:80/api/sensors_data?time_period=<time_in_seconds>
@app.route('/api/sensors_data')
def sensors_data():
    arguments = request.args

    time_period = arguments.get("time_period", None, type=int)

    if time_period == None:
        return ErrorResponse("No time_period provided or it is incorrect", 400)

    air_raw_data, ground_raw_data = db.get_all_data(time_period)

    air = [
        [[], [], []],
        [[], [], []],
        [[], [], []],
        [[], [], []],
        [[], [], []]
    ]

    ground = [
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []],
        [[], []]
    ]

    for sensor_id, temp, hum, timestamp in air_raw_data:
        idx = sensor_id - 1
        air[idx][0].append(temp)
        air[idx][1].append(hum)
        air[idx][2].append(timestamp)

    for sensor_id, humidity, timestamp in ground_raw_data:
        idx = sensor_id - 1
        ground[idx][0].append(humidity)
        ground[idx][1].append(timestamp)

    result = {
        "air": air,
        "ground": ground
    }

    return SuccessResponse(result)

# http://127.0.0.1:80/api/state
@app.route('/api/state')
def cur_state():
    return SuccessResponse(settings)

# http://127.0.0.1:80/api/parameters
@app.route('/api/parameters', methods=['PATCH'])
def parameters():
    data : dict = request.get_json()

    check_parameters(data, (("T", float),("H", float),("Hb", float)))

    T =  data.get("T", None)
    H =  data.get("H", None)
    Hb =  data.get("Hb", None)
    
    if H < 0 or H > 100:
        return ErrorResponse("field \"H\" incorrect", 400)

    if Hb < 0 or Hb > 100:
        return ErrorResponse("field \"Hb\" incorrect", 400)

    settings["parameters"]["T"] = T
    settings["parameters"]["H"] = H
    settings["parameters"]["Hb"] = Hb

    return SuccessResponse(settings["parameters"])

# http://127.0.0.1:80/api/fork_drive
@app.route('/api/fork_drive', methods=['PATCH'])
def fork_drive():
    data = request.get_json()

    check_parameters(data, (("state", int),))

    state =  data.get("state", None)
    
    if state in range(0, 2) == False:
        return ErrorResponse("field \"state\" incorrect", 400)

    if state != settings["fork_drive"]:
        parameters = {
            "state": state
        }

        resp = requests.patch(config.url_patch_fork_drive, params=parameters)
        if resp.status_code == 200:
            settings["fork_drive"] = state
        else:
            return ErrorResponse("Unable to do patch request to greenhouse", 500)

    return SuccessResponse({"state": settings["fork_drive"]})

# http://127.0.0.1:80/api/total_hum
@app.route('/api/total_hum', methods=['PATCH'])
def total_hum():
    data = request.get_json()

    check_parameters(data, (("state", int),))

    state =  data.get("state", None)
    if state in range(0, 2) == False:
        return ErrorResponse("field \"state\" incorrect", 400)

    if state != settings["total_hum"]:
        parameters = {
            "state": state
        }

        resp = requests.patch(config.url_patch_total_hum, params=parameters)
        if resp.status_code == 200:
            settings["total_hum"] = state
        else:
            return ErrorResponse("Unable to do patch request to greenhouse", 500)

    return SuccessResponse({"state": settings["total_hum"]})

# http://127.0.0.1:80/api/emergency
@app.route('/api/emergency', methods=['PATCH'])
def emergency():
    data = request.get_json()

    check_parameters(data, (("state", int),))

    emergency_state = data["state"]
    if emergency_state in range(0, 2):
        settings["emergency"] = emergency_state

    return SuccessResponse({"state": settings["emergency"]})

# http://127.0.0.1:80
@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':

    t = threading.Thread(target=asyncio.run, args=(collector.infinite_collect(),))
    t.start()

    app.run(debug=False,  port=80, host="0.0.0.0")

    print("flask ended")

    collector.end_working = True
