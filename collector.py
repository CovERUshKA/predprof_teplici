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

def infinite_collect():
    print("Collector started")

    while True:
        for i in range(6):
            ground_humidity = get_ground_hum(i+1)

            print(i+1, ground_humidity)

            db.add_ground_hum(ground_humidity)

        for i in range(4):
            air_temperature, air_humidity = get_air_temp_hum(i+1)

            print(i+1, air_temperature, air_humidity)

            db.add_air_temp_hum(air_temperature, air_humidity)

        time.sleep(5)
