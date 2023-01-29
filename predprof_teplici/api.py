import requests
from . import greenhouse_api
from predprof_teplici import database as db

from flask import (
    Blueprint, request, make_response, jsonify, abort, current_app
)

bp = Blueprint('api', __name__, url_prefix='/api')

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
@bp.route('/sensors_data')
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
@bp.route('/state')
def cur_state():
    return SuccessResponse(current_app.config["settings"])

# http://127.0.0.1:80/api/parameters
@bp.route('/parameters', methods=['PATCH'])
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

    current_app.config["settings"]["parameters"]["T"] = T
    current_app.config["settings"]["parameters"]["H"] = H
    current_app.config["settings"]["parameters"]["Hb"] = Hb

    return SuccessResponse(current_app.config["settings"]["parameters"])

# http://127.0.0.1:80/api/fork_drive
@bp.route('/fork_drive', methods=['PATCH'])
def fork_drive():
    data = request.get_json()

    check_parameters(data, (("state", int),))

    state =  data.get("state", None)
    
    if not state in range(0, 2):
        return ErrorResponse("field \"state\" incorrect", 400)

    if state != current_app.config["settings"]["fork_drive"]:
        parameters = {
            "state": state
        }

        resp = requests.patch(greenhouse_api.url_patch_fork_drive, params=parameters)
        if resp.status_code == 200:
            current_app.config["settings"]["fork_drive"] = state
        else:
            return ErrorResponse("Unable to do patch request to greenhouse", 500)

    return SuccessResponse({"state": current_app.config["settings"]["fork_drive"]})

# http://127.0.0.1:80/api/total_hum
@bp.route('/total_hum', methods=['PATCH'])
def total_hum():
    data = request.get_json()

    check_parameters(data, (("state", int),))

    state =  data.get("state", None)
    if not state in range(0, 2):
        return ErrorResponse("field \"state\" incorrect", 400)

    if state != current_app.config["settings"]["total_hum"]:
        parameters = {
            "state": state
        }

        resp = requests.patch(greenhouse_api.url_patch_total_hum, params=parameters)
        if resp.status_code == 200:
            current_app.config["settings"]["total_hum"] = state
        else:
            return ErrorResponse("Unable to do patch request to greenhouse", 500)

    return SuccessResponse({"state": current_app.config["settings"]["total_hum"]})

# http://127.0.0.1:80/api/watering
@bp.route('/watering', methods=['PATCH'])
def watering():
    data = request.get_json()

    check_parameters(data, (("id", int), ("state", int)))

    id =  data.get("id", None)
    if not id in range(1, 7):
        return ErrorResponse("field \"id\" incorrect", 400)

    state =  data.get("state", None)
    if not state in range(0, 2):
        return ErrorResponse("field \"state\" incorrect", 400)

    if state != current_app.config["settings"]["watering"][id - 1]:
        parameters = {
            "id": id,
            "state": state
        }

        resp = requests.patch(greenhouse_api.url_patch_watering, params=parameters)
        if resp.status_code == 200:
            current_app.config["settings"]["watering"][id - 1] = state
        else:
            return ErrorResponse("Unable to do patch request to greenhouse", 500)

    resp_data = {
        "id": id,
        "state": state
    }

    return SuccessResponse(resp_data)

# http://127.0.0.1:80/api/watering
@app.route('/api/watering', methods=['PATCH'])
def watering():
    data = request.get_json()

    check_parameters(data, (("id", int), ("state", int)))

    id =  data.get("id", None)
    if not id in range(1, 7):
        return ErrorResponse("field \"id\" incorrect", 400)

    state =  data.get("state", None)
    if not state in range(0, 2):
        return ErrorResponse("field \"state\" incorrect", 400)

    if state != settings["watering"][id - 1]:
        parameters = {
            "id": id,
            "state": state
        }

        resp = requests.patch(config.url_patch_watering, params=parameters)
        if resp.status_code == 200:
            settings["watering"][id - 1] = state
        else:
            return ErrorResponse("Unable to do patch request to greenhouse", 500)

    resp_data = {
        "id": id,
        "state": state
    }

    return SuccessResponse(resp_data)

# http://127.0.0.1:80/api/emergency
@bp.route('/emergency', methods=['PATCH'])
def emergency():
    data = request.get_json()

    check_parameters(data, (("state", int),))

    emergency_state = data["state"]
    if emergency_state in range(0, 2):
        current_app.config["settings"]["emergency"] = emergency_state

    return SuccessResponse({"state": current_app.config["settings"]["emergency"]})
