import json

from flask import Flask, render_template
from flask_cors import CORS

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    
    #app.config.from_file("config.json", load=json.load)
    f = open("instance/config.json")
    data = json.load(f)
    app.config["urls"] = data

    app.config["settings"] = {
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

    # http://127.0.0.1:80
    @app.route('/')
    def index():
        return render_template("index.html")

    from predprof_teplici import api
    app.register_blueprint(api.bp)

    return app
