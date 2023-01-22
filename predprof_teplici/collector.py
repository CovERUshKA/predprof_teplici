import time
import config
import aiohttp
import asyncio
import database as db

end_working = False

# Влажность почвы
async def get_ground_hum(session : aiohttp.ClientSession, id):
    async with session.get(f"{config.url_get_hum}/{id}") as resp:
        jsoned = {}
        if resp.status == 200:
            jsoned = await resp.json(content_type=None)
            if jsoned == None:
                jsoned = {}
        humidity = jsoned.get("humidity", None)
        return humidity

# Влажность и температура воздуха
async def get_air_temp_hum(session : aiohttp.ClientSession, id):
    async with session.get(f"{config.url_get_temp_hum}/{id}") as resp:
        jsoned = {}
        if resp.status == 200:
            jsoned = await resp.json(content_type=None)
            if jsoned == None:
                jsoned = {}
        humidity = jsoned.get("humidity", None)
        temperature = jsoned.get("temperature", None)
        return temperature, humidity

async def infinite_collect():
    print("Collector started")

    async with aiohttp.ClientSession() as session:
        while end_working == False:

            tasks = []
            for sensor_id in range(1, 7):
                tasks.append(asyncio.ensure_future(get_ground_hum(session, sensor_id)))

            for sensor_id in range(1, 5):
                tasks.append(asyncio.ensure_future(get_air_temp_hum(session, sensor_id)))

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
                avg_temp = sum(temps) / len(temps)
            if len(hums) != 0:
                avg_hum = sum(hums) / len(hums)

            db.add_data_from_sensors(all_ground_humidity, all_air_temp_hum, avg_temp, avg_hum, time_collected)

            time.sleep(5)
    
    print("Collector ended")
