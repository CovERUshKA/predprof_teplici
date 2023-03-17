import sqlite3
import requests
from . import greenhouse_api
from .responses import SuccessResponse, ErrorResponse
from . import database as db

from flask import (
    Blueprint, request, abort, current_app
)

bp = Blueprint('api', __name__, url_prefix='/api')

def check_parameters(data, parameters):
    try:
        assert type(data) == dict, ('data', 404)

        for param in parameters:
            types = param[1:]
            if param[0] in data:
                assert type(data.get(param[0])) in types, (param[0], 400)
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

    check_parameters(data, (("T", float, int),("H", float, int),("Hb", float, int)))

    T = data.get("T", None)
    H = data.get("H", None)
    Hb = data.get("Hb", None)
    
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

    state = data.get("state", None)
    
    if not state in range(0, 2):
        return ErrorResponse("field \"state\" incorrect", 400)

    if state != current_app.config["settings"]["fork_drive"]:
        headers = {
            "X-Auth-Token": greenhouse_api.auth_token
        }

        parameters = {
            "state": state
        }

        resp = requests.patch(greenhouse_api.url_patch_fork_drive, headers=headers, params=parameters)
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

    state = data.get("state", None)
    if not state in range(0, 2):
        return ErrorResponse("field \"state\" incorrect", 400)

    if state != current_app.config["settings"]["total_hum"]:
        headers = {
            "X-Auth-Token": greenhouse_api.auth_token
        }

        parameters = {
            "state": state
        }

        resp = requests.patch(greenhouse_api.url_patch_total_hum, headers=headers, params=parameters)
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

    id = data.get("id", None)
    if not id in range(1, 7):
        return ErrorResponse("field \"id\" incorrect", 400)

    state = data.get("state", None)
    if not state in range(0, 2):
        return ErrorResponse("field \"state\" incorrect", 400)

    if state != current_app.config["settings"]["watering"][id - 1]:
        headers = {
            "X-Auth-Token": greenhouse_api.auth_token
        }

        parameters = {
            "id": id,
            "state": state
        }

        resp = requests.patch(greenhouse_api.url_patch_watering, headers=headers, params=parameters)
        if resp.status_code == 200:
            current_app.config["settings"]["watering"][id - 1] = state
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

# http://127.0.0.1:80/api/add_data
@bp.route('/add_data', methods=['POST'])
def add_data():
    data = request.get_json()

    check_parameters(data, (("air", list), ("ground", list)))

    air_data = data.get("air", None)
    if len(air_data) != 4:
        return ErrorResponse("field \"air\" incorrect", 400)

    for sensor_data in air_data:
        if (type(sensor_data) != list
            or (type(sensor_data[0]) != float and type(sensor_data[0]) != int)
            or (type(sensor_data[1]) != float and type(sensor_data[1]) != int)):
            return ErrorResponse("field \"air\" incorrect", 400)

    ground_data = data.get("ground", None)
    if len(ground_data) != 6:
        return ErrorResponse("field \"ground\" incorrect", 400)

    for ground_hum in ground_data:
        if type(ground_hum) != float and type(ground_hum) != int:
            return ErrorResponse("field \"ground\" incorrect", 400)

    temps = [sensor_data[0] for sensor_data in air_data]
    hums = [sensor_data[1] for sensor_data in air_data]

    avg_temp = round(sum(temps) / len(temps), 2)
    avg_hum = round(sum(hums) / len(hums), 2)
        
    try:
        db.add_data_from_sensors(ground_data, air_data, avg_temp, avg_hum)
    except sqlite3.IntegrityError as e:
        print("Error: ", e)

    return SuccessResponse({})
