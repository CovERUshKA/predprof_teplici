from predprof_teplici.api import check_parameters
from flask.testing import FlaskClient
from flask import Flask
import pytest

def test_check_parameters(client : FlaskClient, app : Flask):
    data = {
        "T": 3,
        "H": 3.23,
        "Hb": 3.3
    }
    try:
        with app.app_context():
            check_parameters(data, (("T", float, int),("H", float, int),("Hb", float, int)))
    except Exception: assert False

    data = {
        "state": "3"
    }
    try:
        with app.app_context():
            check_parameters(data, (("state", int),))
        pytest.fail()
    except Exception: pass

    data = {
        "T": "3",
        "H": 3,
        "Hb": 3
    }
    try:
        with app.app_context():
            check_parameters(data, (("T", float, int),("H", float, int),("Hb", float, int)))
        pytest.fail()
    except Exception: pass

    try:
        with app.app_context():
            check_parameters(None, (("T", float, int),("H", float, int),("Hb", float, int)))
        pytest.fail()
    except Exception: pass
