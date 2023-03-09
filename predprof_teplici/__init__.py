import json

from flask import Flask, render_template
from flask_cors import CORS

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)

    app.config["settings"] = {
        "parameters": {
            "T": None,
            "H": None,
            "Hb": None
        },
        "fork_drive": 0,
        "total_hum": 0,
        "emergency": 0,
        "watering": [0, 0, 0, 0, 0, 0]
    }

    # http://127.0.0.1:80
    @app.route('/')
    def index():
        return render_template("index.html")

    import api
    app.register_blueprint(api.bp)

    return app
