import threading
import collector
import database as db
import asyncio
import time
import requests
import config

from flask import Flask, jsonify, request, abort, make_response

app = Flask(__name__)

def SuccessResponse(result):
    response = {"ok":True, "result":result}

    return jsonify(response)

#{
#   ok: false,
#   error_code: error_code,
#   description: "wewewe"
#}
def ErrorResponse(description, error_code):
    response = {"ok":False, "error_code":error_code, "description":description}

    return jsonify(response), error_code

state = {
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

def check_parameters(data, parameters):
    try:
        assert isinstance(data, dict), 'data'

        for param in parameters:
            if param[0] in data == False:
                assert isinstance(data.get(param[0]), param[1]), param[0]
    except AssertionError as e:
        abort(make_response(jsonify({"error": f"field \"{e}\" incorrect"}), 404))

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

    response = {
        "air": air,
        "ground": ground
    }

    return SuccessResponse(response)

# http://127.0.0.1:80/api/state
@app.route('/api/state')
def cur_state():
    return jsonify(state)

# http://127.0.0.1:80/api/parameters
@app.route('/api/parameters', methods=['PATCH'])
def parameters():
    data : dict = request.get_json()

    check_parameters(data, (("T", float),("H", float),("Hb", float)))

    T =  data.get("T", None)
    H =  data.get("H", None)
    Hb =  data.get("Hb", None)
    
    if H < 0 or H > 100:
        abort(make_response(jsonify({"error": f"field \"H\" incorrect"}), 400))

    if Hb < 0 or Hb > 100:
        abort(make_response(jsonify({"error": f"field \"Hb\" incorrect"}), 400))

    state["parameters"]["T"] = T
    state["parameters"]["H"] = H
    state["parameters"]["Hb"] = Hb

    return jsonify(state["parameters"])

# http://127.0.0.1:80/api/fork_drive
@app.route('/api/fork_drive', methods=['PATCH'])
def fork_drive():
    data = request.get_json()

    check_parameters(data, (("state", int),))

    state =  data.get("state", None, type=int)
    
    if state in range(0, 2) == False:
        abort(make_response(jsonify({"error": f"field \"state\" incorrect"}), 400))

    if state != state["fork_drive"]:
        body = {
            "state": state
        }

        resp = requests.patch(config.url_fork_drive, json=body)
        if resp.status_code == 200 or config.test_mode:
            state["fork_drive"] = state

    return jsonify({"state": state["fork_drive"]})

# http://127.0.0.1:80/api/total_hum
@app.route('/api/total_hum', methods=['PATCH'])
def total_hum():
    data = request.get_json()

    check_parameters(data, (("state", int),))

    state =  data.get("state", None, type=int)
    if state in range(0, 2) == False:
        abort(make_response(jsonify({"error": f"field \"state\" incorrect"}), 400))

    if state != state["total_hum"]:
        body = {
            "state": state
        }

        resp = requests.patch(config.url_total_hum, json=body)
        if resp.status_code == 200 or config.test_mode:
            state["total_hum"] = state

    state["total_hum"] = state

    return jsonify({"state": state["total_hum"]})

# http://127.0.0.1:80/api/emergency
@app.route('/api/emergency', methods=['PATCH'])
def emergency():
    data = request.get_json()

    check_parameters(data, (("state", int),))

    emergency_state = data["state"]
    if emergency_state in range(0, 2):
        state["emergency"] = emergency_state

    return jsonify({"state": state["emergency"]})

@app.route('/')
def index():
    return "Hello, World!"

if __name__ == '__main__':

    t = threading.Thread(target=asyncio.run, args=(collector.infinite_collect(),))
    t.start()

    app.run(debug=False,  port=80, host="0.0.0.0")

    print("flask ended")

    collector.end_working = True
