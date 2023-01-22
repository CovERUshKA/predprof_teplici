import threading
import sqlite3
import time

lock = threading.Lock()

# Подключаемся к файлу базы данных
con = sqlite3.connect("main.db", check_same_thread=False)
# Берём управление базой данных
cur = con.cursor()

# Создаём таблицу данных земли, если не создана
cur.execute("create table if not exists ground (id INTEGER PRIMARY KEY AUTOINCREMENT, sensor_id INTEGER NOT NULL, humidity FLOAT NOT NULL, timestamp BIGINT NOT NULL)")

# Создаём таблицу данных воздуха, если не создана
cur.execute("create table if not exists air (id INTEGER PRIMARY KEY AUTOINCREMENT, sensor_id INTEGER NOT NULL, temperature FLOAT NOT NULL, humidity FLOAT NOT NULL, timestamp BIGINT NOT NULL)")

def execute_and_commit(sql, parameters = ()):
    """Выполняем sql команду и сразу сохраняем её в файл"""

    try:
        lock.acquire(True)

        cur.execute(sql, parameters)
        con.commit()
    finally:
        lock.release()

    return

def execute_and_fetchall(sql, parameters = ()):
    """Выполняем sql команду и сразу возвращаем результат"""

    try:
        lock.acquire(True)

        cur.execute(sql, parameters)
        ret = cur.fetchall()
    finally:
        lock.release()

    return ret

def add_ground_hums(sensor_id, humidities, time_collected):
    """Добавляем данные о влажности земли"""

    if humidity == None:
        humidity = 0

    if sensor_id == None:
        raise Exception(("No air sensor id"))

    if time_collected == None:
        raise Exception(("No time when ground hum data been collected"))
    
    execute_and_commit("INSERT into ground (humidity, timestamp) values (?, ?)", (humidity, time_collected))

    return True

def add_air_temp_hum(sensor_id, temperature, humidity, time_collected):
    """Добавляем данные о температуре и влажности воздуха"""

    if sensor_id == None:
        raise Exception(("No air sensor id"))

    if temperature == None:
        temperature = 0

    if humidity == None:
        humidity = 0

    if time_collected == None:
        raise Exception(("No time when data been collected"))

    execute_and_commit("INSERT into air (sensor_id, temperature, humidity, timestamp) values (?, ?, ?)", (sensor_id, temperature, humidity, time_collected))

    return True

def add_data_from_sensors(ground_humidities, air_temps_hums, avg_temp, avg_hum, time_collected):
    """Добавляем данные со всех датчиков в БД"""

    if ground_humidities == None:
        raise Exception(("No ground humidities to add"))
    elif len(ground_humidities) != 6:
        raise Exception((f"Incorrect count of ground humidities: {len(ground_humidities)}"))

    if air_temps_hums == None:
        raise Exception(("No air temperatures and humidites to add"))
    elif len(air_temps_hums) != 4:
        raise Exception((f"Incorrect count of ground humidities: {len(air_temps_hums)}"))

    if time_collected == None:
        raise Exception(("No time when data been collected"))

    try:
        lock.acquire(True)

        for i in range(6):
            cur.execute("INSERT into ground (sensor_id, humidity, timestamp) values (?, ?, ?)", (i+1, ground_humidities[i], time_collected))

        for i in range(4):
            cur.execute("INSERT into air (sensor_id, temperature, humidity, timestamp) values (?, ?, ?, ?)", (i+1, air_temps_hums[i][0], air_temps_hums[i][1], time_collected))

        cur.execute("INSERT into air (sensor_id, temperature, humidity, timestamp) values (?, ?, ?, ?)", (5, avg_temp, avg_hum, time_collected))
        
        con.commit()
    finally:
        lock.release()

    return True

def get_air_temp_hum(time_period):
    """Добавляем данные о температуре и влажности воздуха"""

    cur_time = round(time.time())

    time_since = cur_time - time_period

    ret = execute_and_fetchall(f"SELECT temperature, humidity, timestamp from air where timestamp > ?", (time_since,))

    return ret

def get_all_data(time_period):
    """Берём данные из базы данных за период времени time_period"""

    cur_time = round(time.time())

    time_since = cur_time - time_period

    try:
        lock.acquire(True)

        cur.execute("SELECT sensor_id, temperature, humidity, timestamp from air where timestamp > ?", (time_since,))
        
        air = cur.fetchall()

        cur.execute("SELECT sensor_id, humidity, timestamp from ground where timestamp > ?", (time_since,))

        ground = cur.fetchall()
    finally:
        lock.release()

    return air, ground
