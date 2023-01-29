import time
from . import greenhouse_api
import aiohttp
import asyncio
import requests
from . import database as db
import sqlite3

end_working = False

def get_air_temp_hum(id):
    response = requests.get(f"{greenhouse_api.url_get_temp_hum}/{id}")
    if response.status_code == 200:
        data = response.json()
        if type(data) == dict:
            temp = data.get("temperature")
            hum = data.get("humidity")
            return temp, hum
    return None, None

# Влажность почвы
async def aget_ground_hum(session : aiohttp.ClientSession, id):
    try:
        async with session.get(f"{greenhouse_api.url_get_hum}/{id}") as resp:
            jsoned = {}
            if resp.status == 200:
                jsoned = await resp.json(content_type=None)
                if jsoned == None:
                    jsoned = {}
            humidity = jsoned.get("humidity", None)
            return humidity
    except aiohttp.ClientError as e:
        return None
# Влажность и температура воздуха
async def aget_air_temp_hum(session : aiohttp.ClientSession, id):
    try:
        async with session.get(f"{greenhouse_api.url_get_temp_hum}/{id}") as resp:
            jsoned = {}
            if resp.status == 200:
                jsoned = await resp.json(content_type=None)
                if jsoned == None:
                    jsoned = {}
            humidity = jsoned.get("humidity", None)
            temperature = jsoned.get("temperature", None)
            return temperature, humidity
    except aiohttp.ClientError as e:
        return None, None

async def infinite_collect():
    print("Collector started")

    async with aiohttp.ClientSession() as session:
        while end_working == False:

            tasks = []
            for sensor_id in range(1, 7):
                tasks.append(asyncio.ensure_future(aget_ground_hum(session, sensor_id)))

            for sensor_id in range(1, 5):
                tasks.append(asyncio.ensure_future(aget_air_temp_hum(session, sensor_id)))

            rets = await asyncio.gather(*tasks)

            all_ground_humidity = rets[0:6]
            all_air_temp_hum = rets[6:10]
            time_collected = round(time.time())

            temps = []
            hums = []

            for temp, hum in all_air_temp_hum:
                if temp != None:
                    temps.append(temp)
                if hum != None:
                    hums.append(hum)

            #TODO: Что будет, если avg_temp или avg_hum будут равны None? Сделать тесты и т.п.
            avg_temp = None
            avg_hum = None

            if len(temps) != 0:
                avg_temp = round(sum(temps) / len(temps), 2)
            if len(hums) != 0:
                avg_hum = round(sum(hums) / len(hums), 2)
                
            try:
                db.add_data_from_sensors(all_ground_humidity, all_air_temp_hum, avg_temp, avg_hum, time_collected)
            except sqlite3.IntegrityError as e:
                print("Error: ", e)
            finally:
                time.sleep(5)
    
    print("Collector ended")
