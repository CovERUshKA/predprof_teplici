import time
import requests
import database as db

# Влажность почвы
def get_ground_hum(id):
    response = requests.get(f"https://dt.miet.ru/ppo_it/api/hum/{id}")
    if response.status_code == 200:
        jsoned = response.json()

        humidity = jsoned.get("humidity", None)
        if humidity != None:
            return humidity
    else:
        print("Unable to get ground humidity of {id} sensor")
        raise Exception("Unable to get ground humidity of {id} sensor")

    return None

# Влажность и температура воздуха
def get_air_temp_hum(id):
    response = requests.get(f"https://dt.miet.ru/ppo_it/api/temp_hum/{id}")
    if response.status_code == 200:
        jsoned = response.json()

        humidity = jsoned.get("humidity", None)

        temperature = jsoned.get("temperature", None)

        return temperature, humidity

    return None, None

# TODO: Add asynchronous request of data

def infinite_collect():
    print("Collector started")

    while True:
        time_collected = round(time.time())

        all_ground_humidity = []

        for i in range(6):
            sensor_id = i+1

            ground_humidity = get_ground_hum(sensor_id)

            all_ground_humidity.append(ground_humidity)

            #print(i+1, ground_humidity)

        all_air_temp_hum = []

        for i in range(4):
            sensor_id = i+1

            air_temperature, air_humidity = get_air_temp_hum(sensor_id)

            all_air_temp_hum.append([air_temperature, air_humidity])

            #print(i+1, air_temperature, air_humidity)

        #db.add_ground_hums(sensor_id, ground_humidity, time_collected)

        #db.add_air_temp_hum(sensor_id, air_temperature, air_humidity, time_collected)

        db.add_data_from_sensors(all_ground_humidity, all_air_temp_hum, time_collected)

        time.sleep(5)
