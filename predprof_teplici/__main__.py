import threading
import collector
import database as db
import asyncio

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

    ret = {
        "air": air,
        "ground": ground
    }

    return SuccessResponse(ret)

@app.route('/')
def index():
    return "Hello, World!"

if __name__ == '__main__':

    t = threading.Thread(target=asyncio.run, args=(collector.infinite_collect(),))
    t.start()

    app.run(debug=False,  port=80, host="0.0.0.0")

    print("flask ended")

    collector.end_working = True
