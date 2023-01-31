from flask.testing import FlaskClient

def test_parameters(client : FlaskClient, app):
    new_parameters = {
        "T": 19.3,
        "H": 13.4,
        "Hb": 39.2,
    }
    response = client.patch("/api/parameters", json=new_parameters)
    assert response.status_code == 200
    assert app.config["settings"]["parameters"] == new_parameters

    new_parameters = {
        "T": 19,
        "H": 13,
        "Hb": 39,
    }
    response = client.patch("/api/parameters", json=new_parameters)
    assert response.status_code == 200
    assert app.config["settings"]["parameters"] == new_parameters

    new_parameters = {
        "T": 19,
        "H": 13,
        "Hb": 39.3,
    }
    response = client.patch("/api/parameters", json=new_parameters)
    assert response.status_code == 200
    assert app.config["settings"]["parameters"] == new_parameters

    new_parameters = {
        "T": 19.3,
        "H": "13.4",
        "Hb": 39.2,
    }
    response = client.patch("/api/parameters", json=new_parameters)
    assert response.status_code == 400

    new_parameters = {
        "T": 19.3,
        "Hb": 39.2,
    }
    response = client.patch("/api/parameters", json=new_parameters)
    assert response.status_code == 404

def test_state(client : FlaskClient, app):
    response = client.get("/api/state")

    assert response.status_code == 200
    assert response.get_json()["result"] == app.config["settings"]

def test_total_hum(client : FlaskClient, app):
    response = client.patch("/api/total_hum", json={
        "state": 1
    })
    assert response.status_code == 200

    response = client.patch("/api/total_hum", json={
        "state": 0
    })
    assert response.status_code == 200

    response = client.patch("/api/total_hum", json={
        "state": None
    })
    assert response.status_code == 400

    response = client.patch("/api/total_hum", json={
        "state": "1"
    })
    assert response.status_code == 400

    response = client.patch("/api/total_hum", json={})
    assert response.status_code == 404

def test_fork_drive(client : FlaskClient, app):
    response = client.patch("/api/fork_drive", json={
        "state": 1
    })
    assert response.status_code == 200

    response = client.patch("/api/fork_drive", json={
        "state": 0
    })
    assert response.status_code == 200

    response = client.patch("/api/fork_drive", json={
        "state": None
    })
    assert response.status_code == 400

    response = client.patch("/api/fork_drive", json={})
    assert response.status_code == 404

def test_watering(client : FlaskClient, app):
    json = {
        "id": 1,
        "state": 1
    }
    response = client.patch("/api/watering", json=json)
    assert response.status_code == 200
    assert app.config["settings"]["watering"][0] == json["state"]

    json = {
        "id": 7
    }
    response = client.patch("/api/watering", json=json)
    assert response.status_code == 404

    json = {
        "id": 7,
        "state": None
    }
    response = client.patch("/api/watering", json=json)
    assert response.status_code == 400

    json = {
        "id": 7,
        "state": "1"
    }
    response = client.patch("/api/watering", json=json)
    assert response.status_code == 400

    json = {
        "id": 1,
        "state": 2
    }
    response = client.patch("/api/watering", json=json)
    assert response.status_code == 400

    json = {
        "id": 7,
        "state": 1
    }
    response = client.patch("/api/watering", json=json)
    assert response.status_code == 400

def test_add_hum(client : FlaskClient, app):
    json = {
        "id": 1,
        "humidity": 11.2
    }
    response = client.post("/api/add_hum", json=json)
    assert response.status_code == 200

    json = {
        "id": 1,
        "humidity": 11
    }
    response = client.post("/api/add_hum", json=json)
    assert response.status_code == 200

    json = {
        "id": 7,
        "humidity": 11.2
    }
    response = client.post("/api/add_hum", json=json)
    assert response.status_code == 400

    json = {
        "id": 1
    }
    response = client.post("/api/add_hum", json=json)
    assert response.status_code == 404

def test_add_temp_hum(client : FlaskClient, app):
    json = {
        "id": 1,
        "temperature": 11.3,
        "humidity": 11.2
    }
    response = client.post("/api/add_temp_hum", json=json)
    assert response.status_code == 200

    json = {
        "id": 1,
        "temperature": 11,
        "humidity": 11.2
    }
    response = client.post("/api/add_temp_hum", json=json)
    assert response.status_code == 200

    json = {
        "id": 1,
        "temperature": 11,
        "humidity": 11
    }
    response = client.post("/api/add_temp_hum", json=json)
    assert response.status_code == 200

    json = {
        "id": 7,
        "temperature": 11.2,
        "humidity": 11.2
    }
    response = client.post("/api/add_temp_hum", json=json)
    assert response.status_code == 400

    json = {
        "id": 1,
        "humidity": 11.2
    }
    response = client.post("/api/add_temp_hum", json=json)
    assert response.status_code == 404

    json = {
        "id": 1,
        "temperature_invalid": 11,
        "humidity": 11.2
    }
    response = client.post("/api/add_temp_hum", json=json)
    assert response.status_code == 404
